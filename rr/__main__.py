import re
from os import path, makedirs, listdir, environ as env, stat
import asyncio
from time import time, sleep
import math
from pathlib import Path
from math import ceil, floor
import subprocess
from multiprocessing import Pool, set_start_method  # , Lock
from functools import partial
from traceback import format_exc
from warnings import filterwarnings
from requests import get

from click import group, argument, option, Choice
from pandas import read_csv
import numpy as np
from pydub import AudioSegment
from music_tag import load_file

# from beep import beep
# from cloud_mail_api import CloudMail
# from fuck import ProfanityHandler
from tqdm import tqdm
# import torch
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import NetworkError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, Defaults, ConversationHandler, CallbackQueryHandler
from telegram.warnings import PTBUserWarning

from much import Fetcher, Exporter, Format, normalize
from karma import CloudMail

# from .Bark import Bark
# from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech
from .Crt import Crt
# from .Coqui import Coqui
from .Silero import Silero

from .RaconteurFactory import RaconteurFactory

from .util import one_is_not_none, read, is_audio  # , drop_accent_marks, drop_empty_lines
from .SpeechIndex import SpeechIndex

from .alternator import _alternate, _alternate_pool_wrapper
from .Thread import Thread

filterwarnings(action = 'ignore', message = r'.*CallbackQueryHandler', category = PTBUserWarning)


# ENGINES = Choice((Bark.name, RuTTS.name, SaluteSpeech.name, Crt.name, Coqui.name, Silero.name), case_sensitive = False)
ENGINES = Choice((SaluteSpeech.name, Crt.name, Silero.name), case_sensitive = False)
OVERLAY = (
    'ffmpeg -y -i {input} -i {background} '
    '-filter_complex "[1:a]atrim=start={offset},asetpts=PTS-STARTPTS,volume={volume}[v1];[0:a][v1]amix=inputs=2:duration=shortest" '
    '-map_metadata 0 -metadata TDOR="2023" -metadata date="2023" {output}'
)
N_MILLISECONDS_IN_SECOND = 1000

TELEGRAM_TOKEN_ENV = 'RACONTEUR_BOT_TOKEN'
CHAT_ID_ENV = 'MY_CHAT_ID'

KARMA_USERNAME_ENV = 'KARMA_USERNAME'
KARMA_PASSWORD_ENV = 'KARMA_PASSWORD'
KARMA_AUTH_TIMEOUT = 1800  # seconds

CATALOG_URL = 'https://2ch.hk/b/catalog.json'
N_TOP_THREADS = 50

FILENAME = 'filename'
BUTTON = 'button'

NEXT_BUTTON = 'next-button'
NEXT = 'next'
PREVIOUS = 'previous'
THREAD = 'thread'
CANCEL = 'cancel'
KEEP = 'keep'
CLEAR = 'clear'

URL_REGEXP = re.compile('http.+')
MAX_URL_LENGTH = 92


@group()
def main():
    pass


@main.command()
@argument('assets', type = str, default = '/tmp')
@option('--cloud', '-c', help = 'path to remote folder in mail ru cloud for uploading generated audio files', type = str, default = None)
def start(assets: str, cloud: str):
    # response = get(CATALOG_URL)

    # if (status_code := response.status_code) != 200:
    #     raise ValueError(f'Can\'t pull threads, response status code is {status_code}')

    # threads = sorted(Thread.from_list(response.json()['threads']), key = lambda thread: thread.length, reverse = True)[:N_TOP_THREADS]
    # for thread in threads:
    #     print(thread)

    # return

    token = env.get(TELEGRAM_TOKEN_ENV)
    chat_id = env.get(CHAT_ID_ENV)

    if cloud is not None:
        karma_username = env.get(KARMA_USERNAME_ENV)
        karma_password = env.get(KARMA_PASSWORD_ENV)

        if karma_username is None or karma_password is None:
            raise ValueError(f'Environment variables {KARMA_USERNAME_ENV} and {KARMA_PASSWORD_ENV} must be set')

        uploader = CloudMail(karma_username, karma_password)
        uploader.auth()
        last_auth_timestamp = time()
    else:
        uploader = None
        last_auth_timestamp = None  # time()

    if not path.isdir(assets):
        makedirs(assets)

    fetcher = Fetcher()
    exporter = Exporter()

    if token is None:
        raise ValueError(f'Environment variable {TELEGRAM_TOKEN_ENV} must be defined')

    if chat_id is None:
        raise ValueError(f'Environment variable {CHAT_ID_ENV} must be defined')
    else:
        chat_id = int(chat_id)

    def get_threads():
        response = get(CATALOG_URL, timeout = 60)

        if (status_code := response.status_code) != 200:
            raise ValueError(f'Can\'t pull threads, response status code is {status_code}')

        return sorted(Thread.from_list(response.json()['threads']), key = lambda thread: thread.length, reverse = True)

    async def _keep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await _next(update, context, delete_last = False)

    async def _next(update: Update, context: ContextTypes.DEFAULT_TYPE, delete_last: bool = True) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        keyboard_line = [
            # InlineKeyboardButton('speak', callback_data = THREAD),
            InlineKeyboardButton('keep', callback_data = KEEP),
            InlineKeyboardButton('quit', callback_data = CANCEL),
            InlineKeyboardButton('clear', callback_data = CLEAR)
        ]
        movement_line = []

        thread_index = context.user_data.get('thread_index')

        if thread_index is None:
            thread_index = 0
            context.user_data['threads'] = threads = get_threads()
        else:
            thread_index += 1
            threads = context.user_data['threads']

        if thread_index > 0:
            movement_line = [InlineKeyboardButton('prev', callback_data = PREVIOUS), *movement_line]

        if thread_index < len(threads) - 1:
            movement_line = [InlineKeyboardButton('next', callback_data = NEXT), *movement_line]

        if thread_index >= len(threads):
            await user.send_message('No more threads')

            # context.user_data.pop('thread_index')
            # context.user_data.pop('threads')
            # context.user_data.pop('last_thread_description_message_id')

            # return ConversationHandler.END
            return NEXT_BUTTON

        if (message_id := context.user_data.get('last_thread_description_message_id')) is not None and delete_last:
            await context.bot.delete_message(message_id = message_id, chat_id = user.id)

        context.user_data['thread_index'] = thread_index

        thread = threads[thread_index]

        buttons = InlineKeyboardMarkup(
            [
                keyboard_line,
                movement_line
            ]
        )

        # message_text = f'{thread.title.replace("<br>", "<br/>")}<br/><br/><b>Length: {thread.length}</b><br/><b>Freshness: {thread.freshness}%</b>'

        files = thread.files

        message_text = f'{thread.link}\n\n{thread.title_text}\n\n{thread.links}\n\n**Length: {thread.length}**\n**Freshness: {100 * thread.freshness:.2f}%**'

        for match in URL_REGEXP.findall(message_text):
            if len(match) > MAX_URL_LENGTH:
                message_text = message_text.replace(match, match[:MAX_URL_LENGTH])

        def cut_message(message: str):
            return message[:4096].replace('_', '\\_')

        try:
            if len(files) > 0 and (file := files[0].link).endswith('png') or file.endswith('jpg') and len(message_text) <= 1024:
                try:
                    message = await user.send_photo(file, caption = message_text, reply_markup = buttons, parse_mode = 'Markdown')
                except:
                    message = await user.send_message(cut_message(message_text), reply_markup = buttons, parse_mode = 'Markdown')
            else:
                message = await user.send_message(cut_message(message_text), reply_markup = buttons, parse_mode = 'Markdown')
        except:
            message = await user.send_message(
                f'Thread {thread.link} is not supported\n\n{thread.links}\n\n**Length: {thread.length}**\n**Freshness: {100 * thread.freshness:.2f}%**',
                reply_markup = buttons,
                parse_mode = 'Markdown'
            )

        context.user_data['last_thread_description_message_id'] = message.message_id

        return NEXT_BUTTON

    async def _previous(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        if (thread_index := context.user_data.get('thread_index')) is None:
            raise ValueError('Missing thread index. Can\'t go back')

        if thread_index < 1:
            await user.send_message('No previous threads')

            return NEXT_BUTTON

        context.user_data['thread_index'] = thread_index - 2

        return await _next(update, context)

    async def _next_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        data = update.callback_query.data

        match data:
            case 'next':
                return await _next(update, context)
            case 'thread':
                return await _thread(update, context)
            case 'cancel':
                return await _next_cancel(update, context)
            case 'previous':
                return await _previous(update, context)
            case 'keep':
                return await _keep(update, context)
            case 'clear':
                if (message_id := context.user_data.get('last_thread_description_message_id')) is not None:
                    await context.bot.delete_message(message_id = message_id, chat_id = user.id)
                return await _next_cancel(update, context, quiet = True)
            case _:
                raise ValueError(f'Unsupported context data: {data}')

    async def _thread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        if 'last_thread_description_message_id' in context.user_data:
            context.user_data.pop('last_thread_description_message_id')

        await user.send_message(f'You have selected thread {context.user_data["thread_index"]}, now send me the filename')

        return FILENAME

    async def _next_filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        # await user.send_message(f'Perfect, your thread is {context.user_data["thread_index"]} and your filename is {update.message.text}. Generating the speech...')
        # await asyncio.get_event_loop().run_in_executor(None, lambda: speak(user, context.user_data['threads'][context.user_data['thread_index']].id, update.message.text))
        # await speak(user, context.user_data['threads'][context.user_data['thread_index']].id, update.message.text)
        # await speak(user, context.user_data['threads'][context.user_data['thread_index']].id, update.message.text)

        if 'last_thread_description_message_id' in context.user_data:
            context.user_data.pop('last_thread_description_message_id')

        thread_id = context.user_data['threads'][context.user_data['thread_index']].id
        text = update.message.text

        context.job_queue.run_once(lambda _: speak(user, thread_id, text, quiet = True), when = 0)

        return await _next(update, context)

    async def _next_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, quiet: bool = False) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        if not quiet:
            await user.send_message('Cancelling the iteration over threads')

        if 'thread_index' in context.user_data:
            context.user_data.pop('thread_index')
        if 'threads' in context.user_data:
            context.user_data.pop('threads')
        if 'last_thread_description_message_id' in context.user_data:
            context.user_data.pop('last_thread_description_message_id')

        return ConversationHandler.END

    async def _top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        try:
            top_n = int(update.message.text[::-1].split(' ', maxsplit = 1)[0][::-1])
        except ValueError:
            top_n = N_TOP_THREADS

        # keyboard = [
        #     [
        #         InlineKeyboardButton('Option 1', callback_data = '1'),
        #         InlineKeyboardButton('Option 2', callback_data = '2')
        #     ],
        #     [
        #         InlineKeyboardButton('Option 3', callback_data = '3')
        #     ]
        # ]

        keyboard = [
            [
                InlineKeyboardButton(f'[{thread.length}] {{{thread.freshness:.2f}}} {thread.header}', callback_data = thread.id)
            ]
            for thread in get_threads()[:top_n]
        ]

        markup = InlineKeyboardMarkup(keyboard)

        # await user.send_message(f'Here will be a menu for choosing a right thread out of top {top_n} threads. Now please send a filename')

        await update.message.reply_text('Please, choose thread to generate speech for:', reply_markup = markup)

        return BUTTON

    async def _button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        query = update.callback_query
        context.user_data['thread_id'] = query.data

        # await user.send_message(f'Ok, called button handler for option {query.data}')
        await user.send_message('Ok, now please send me the filename')

        return FILENAME

    async def _filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        message = update.message.text
        # await user.send_message(f'Fine, got your file name. Saving thread {context.user_data["thread_id"]} as "{message}"')
        await speak(user, context.user_data['thread_id'], message)

        return ConversationHandler.END

    async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user

        if user.id != chat_id:
            return

        await user.send_message('Cancelling the last operation')

        return ConversationHandler.END

    async def speak(user, thread_id: int, thread_title: str, url = None, quiet: bool = False):
        nonlocal last_auth_timestamp

        # await asyncio.sleep(5)
        # await user.send_message('Has slept enough')

        # return

        if not quiet:
            await user.send_message(f'Generating speech for thread {thread_id}. Please wait')

        if url is None:
            url = f'https://2ch.hk/b/res/{thread_id}.html'

        filename = thread_id if thread_title is None else thread_title.lower().replace(' ', '-')

        text_path = path.join(assets, f'{filename}.txt')
        audio_path = path.join(assets, f'{filename}.mp3')

        if not path.isfile(text_path):
            print(f'Pulling url {url}...')

            exporter.export(fetcher.fetch(url), Format.TXT, text_path)

            print(f'Pulled {url} to {text_path}. Generating speech...')

        if stat(text_path).st_size == 0:
            await user.send_message(f'Thread {thread_id} does not exist')
        else:
            if not path.isfile(audio_path):
                try:
                    # raise ValueError('test')
                    await asyncio.get_event_loop().run_in_executor(None, lambda: _alternate(text_path, artist_one = 'xenia', artist_two = 'baya'))
                except:
                    await user.send_message(f'There was an internal error:\n\n```{format_exc()}```\nPlease try again', parse_mode = 'Markdown')
                    return

            with open(audio_path, 'rb') as audio_file:
                try:
                    await user.send_audio(audio_file, title = thread_title)
                except NetworkError:
                    await user.send_message(f"Can't send file `{audio_path}` due to a network error:\n\n```{format_exc()}```\nPlease try again", parse_mode = 'Markdown')

            # print(time() - last_auth_timestamp)

            if uploader is not None:
                if ((current_time := time()) - last_auth_timestamp) > KARMA_AUTH_TIMEOUT:
                    uploader.auth()
                    last_auth_timestamp = current_time

                response = uploader.api.file.add(audio_path, path.join(cloud, path.basename(audio_path)))

                print('File uploading result:')
                print(response)

                if response['status'] != 200:
                    await user.send_message(f'There was an internal error when pushing the generated audio file to cloud:\n\n```{response}```', parse_mode = 'Markdown')

    async def _speak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # await update.effective_user.send_message(f'Started handling message {update.message.text}')
        # # print(f'Started handling message {update.message.text}')

        # await asyncio.sleep(5)

        # # await update.effective_user.send_message(f'Stopped handling message {update.message.text}')
        # print(f'Stopped handling message {update.message.text}')

        user = update.effective_user

        if user.id != chat_id:
            return

        message = update.message.text
        # parts = normalize(message.replace('/speak', '').replace('/s', '').strip()).split(' ', maxsplit = 1)
        parts = normalize(message.strip()).split(' ', maxsplit = 1)

        thread_id = parts[0]
        url = None

        if len(parts) > 1:
            thread_title = parts[1]
        else:
            thread_title = None

        if thread_id.startswith('http'):
            url = thread_id
            thread_id = Path(url).stem

        try:
            thread_id = int(thread_id)
        except ValueError:
            await user.send_message(f'Unsupported thread id: {thread_id}')
            return

        await speak(user, thread_id, thread_title, url)

    bot = ApplicationBuilder().token(token).defaults(Defaults(block = False)).build()

    bot.add_handler(
        ConversationHandler(
            entry_points = [CommandHandler('top', _top)],
            states = {
                BUTTON: [CallbackQueryHandler(_button)],
                FILENAME: [MessageHandler(~filters.COMMAND, _filename)]
            },
            fallbacks = [CommandHandler('cancel', _cancel)]
        )
    )

    bot.add_handler(
        ConversationHandler(
            entry_points = [CommandHandler('next', _next)],
            states = {
                NEXT: [CallbackQueryHandler(_next)],
                NEXT_BUTTON: [CallbackQueryHandler(_next_button), MessageHandler(~filters.COMMAND, _next_filename)],
                # THREAD: [CallbackQueryHandler(_thread)],
                FILENAME: [MessageHandler(~filters.COMMAND, _next_filename)]
            },
            fallbacks = [CommandHandler('cancel', _next_cancel)]
        )
    )

    # bot.add_handler(CommandHandler('speak', _speak))
    # bot.add_handler(CommandHandler('s', _speak))
    # bot.add_handler(MessageHandler(filters.Regex(re.compile('http.+', re.IGNORECASE)), _speak))

    bot.add_handler(MessageHandler(filters.ALL, _speak))

    print('Started telegram bot')
    bot.run_polling()


@main.command()
@argument('source', type = str)
@argument('background', type = str)
@argument('destination', type = str)
@option('--volume', '-v', type = float, default = 0.2)
def overlay(source: str, background: str, destination: str, volume: float):
    offset = 0
    background_length = floor(len(AudioSegment.from_mp3(background)) / N_MILLISECONDS_IN_SECOND)

    if not path.isdir(destination):
        makedirs(destination)

    for filename in tqdm(sorted(listdir(source))):
        file = path.join(source, filename)

        if is_audio(file):
            source_meta = load_file(file)
            file_length = ceil(len(AudioSegment.from_mp3(file)) / N_MILLISECONDS_IN_SECOND)

            if offset + file_length > background_length:
                offset = 0

            overlay_ = OVERLAY.format(
                input = file,
                background = background,
                offset = offset,
                volume = volume,
                output = (destination_file := path.join(destination, filename))
            )

            subprocess.call(overlay_, shell = True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            # subprocess.call(overlay_, shell = True)

            destination_meta = load_file(destination_file)

            destination_meta['lyrics'] = source_meta['lyrics']
            destination_meta['comment'] = source_meta['comment']
            # destination_meta['album'] = source_meta['album']

            destination_meta.save()

            offset += file_length


@main.command()
@argument('texts', type = str)
@argument('output_path', type = str)
@option('--artist-one', '-a1', help = 'ifrst artist to say the replic', default = 'xenia')
@option('--artist-two', '-a2', help = 'second artist to say the replic', default = 'baya')
@option('--n-workers', '-w', help = 'how many processes to deploy for mapping the objects', default = 4)
@option('--limit', '-l', type = int, help = 'how many files to process in total', default = None)
def iterate(texts: str, output_path: str, artist_one: str, artist_two: str, n_workers: int, limit: int):
    set_start_method('spawn', force = True)

    def generate_samples():
        for file in listdir(texts):
            input_file = path.join(texts, file)
            output_file = path.join(output_path, f'{path.splitext(file)[0]}.mp3')

            if path.isfile(output_file):
                continue

            yield (input_file, output_file)

    items = tuple(generate_samples())

    if limit is not None:
        items = items[:limit]

    print(f'Processing {len(items)} items...')

    # pbar = tqdm(total = len(items))

    # apply = partial(_alternate_pool_wrapper, artist_one = artist_one, artist_two = artist_two, pbar = pbar, lock = lock)
    apply = partial(_alternate_pool_wrapper, artist_one = artist_one, artist_two = artist_two)

    with Pool(processes = n_workers) as pool:
        pool.map(apply, items)

    # for inp, outp in generate_samples():
    #     print(inp, outp)
    #     return


@main.command()
@argument('text', type = str)  # file must be in a format exported by much module: see https://github.com/zeionara/much
@option('--artist-one', '-a1', help = 'first artist to say the replic', default = 'xenia')
@option('--artist-two', '-a2', help = 'second artist to say the replic', default = 'baya')
def alternate(text: str, artist_one: str, artist_two: str):
    _alternate(text, artist_one, artist_two)


@main.command()
@argument('text', type = str, required = False)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = Silero.name)
@option('--destination', '-d', help = 'path to the resulting mp3 file', type = str, default = None)
@option('--russian', '-r', help = 'is input text in russian language', is_flag = True)
@option('--txt', '-t', help = 'read text from a plain .txt file located at the given path', type = str, default = None)
@option('--artist', '-a', help = 'speaker id to use for speech generation', type = str, default = None)
@option('--drop-text', '-x', help = 'do not keep source text in generated audio file metadata (for instance, because the text is very long)', is_flag = True)
@option('--batch-size', '-b', help = 'number of characters per generated audio file', type = int, default = None)
@option('--ssml', '-m', help = 'does input text contain ssml tags', is_flag = True)
@option('--first-batch-index', '-f', help = 'in a multibatch setting from what number to start enumerating the batches', type = int, default = 0)
@option('--update', '-u', help = 'update existing files instead of generating new ones', is_flag = True)
def say(
    text: str, max_n_characters: int, gpu: bool, engine: str, destination: str, russian: bool, txt: str, artist: str,
    drop_text: bool, batch_size: int, ssml: bool = False, first_batch_index: int = 0, update: bool = True
):
    match one_is_not_none('Exactly one of input text, path to txt file must be specified', text, txt):
        case 1:
            text = read(txt)

    if batch_size is not None:
        if destination is None:
            txt_stem = Path(txt).stem
            destination = path.join(txt[::-1].split('/', maxsplit = 1)[1][::-1], txt_stem)

            # print(destination)
            # raise ValueError('Destination name is required when splitting output file')

        n_chunks = first_batch_index + math.ceil(len(text) / batch_size)

        # val = input(f'There will be {n_chunks} chunks, ok? (y/N): ')

        # if val != 'y':
        #     return

        if not path.isdir(destination):
            makedirs(destination)

        stem = Path(destination).stem
        batch_index_max_length = len(str(n_chunks))
        # template = "f'" + path.join(destination, f'{stem}-{{batch:0{batch_index_max_length}d}}.mp3') + "'"

        title = f'{stem}-{{batch:0{batch_index_max_length}d}}'
        template = path.join(destination, f'{title}.mp3')

        destination = template

        # batch = 8
        # print(eval(template))

        # print(template.format(batch = 8))

    else:
        if destination is None:
            destination = 'assets/speech.mp3'

        if not path.isdir('assets'):
            makedirs('assets')

        title = None

    RaconteurFactory(gpu, russian).make(engine, max_n_characters, artist, ssml).speak(
        text, filename = destination, pbar = True, save_text = not drop_text, batch_size = batch_size, first_batch_index = first_batch_index, title = title, update = update
    )


@main.command()
@option('--source', '-s', help = 'path to the input tsv file with anecdotes', type = str, default = 'assets/anecdotes.tsv')
@option('--destination', '-d', help = 'path to the output directory with anecdotes', type = str, default = 'assets/anecdotes')
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--top-n', '-n', help = 'number of entries to handle', type = int, default = None)
@option('--offset', '-o', help = 'number of entries in the beginning to skip', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = Silero.name)
@option('--russian', '-r', help = 'is input text in russian language', is_flag = True)
@option('--skip-if-exists', '-k', help = 'skip anek if audio file with the same name already exists', is_flag = True)
@option('--username', '-u', help = 'cloud mail ru username', type = str)
@option('--password', '-p', help = 'cloud mail ru password', type = str)
@option('--cloud-root', '-x', help = 'root folder where to upload generated mp3 files', type = str)
@option('--upload-and-quit', '-q', help = 'upload files to cloud if they exist before starting speech generation', is_flag = True)
@option('--verbose', '-v', help = 'whether to enable additional logging', is_flag = True)
def handle_aneks(
    source: str, destination: str, max_n_characters: int, top_n: int, offset: int, gpu: bool, engine: str, russian: bool, skip_if_exists: bool,
    username: str, password: str, cloud_root: str, upload_and_quit: bool, verbose: bool
):
    if not path.isdir(destination):
        makedirs(destination)

    df = read_csv(source, sep = '\t')

    n_aneks = 0

    speaker = RaconteurFactory(gpu, russian).make(engine, max_n_characters)

    cm = None

    if username is not None and password is not None and cloud_root is not None:
        cm = CloudMail(username, password)
        cm.auth()

    start = time()

    with beep():
        for _, row in (
            (
                df if offset is None else df.iloc[offset:,]
            )
            if top_n is None else
            (
                df.iloc[:top_n,] if offset is None else df.iloc[offset:top_n,]
            )
        ).loc[:, ('id', 'text', 'source')].iterrows():
            text = row['text']

            name = f'{row["id"]:08d}.{row["source"]}.mp3'
            # name_copy = f'{row["id"]:08d}.{row["source"]} (1).mp3'
            filename = path.join(destination, name)

            # print(f'Handling "{text}"')
            if upload_and_quit and cm is not None and path.isfile(filename):
                # print(filename, f'{cloud_root}/{name}')
                status = None

                while status != 200:
                    response = cm.api.file.add(filename, f'{cloud_root}/{name}')
                    status = response['status']

                # response = cm.api.file(f'{cloud_root}/{name}')

                # if response['status'] != 200:
                #     print(response)

                # cm.api.file.remove(f'{cloud_root}/{name_copy}')

            if not skip_if_exists or not path.isfile(filename):
                if verbose:
                    print(text)

                # try:
                speaker.speak(
                    text = text,
                    filename = filename
                )
                # except Exception:  # on any exception try to repeat again after 10 seconds, there may be a temporary problem with the network
                #     sleep(10)

                #     speaker.speak(
                #         text = text,
                #         filename = filename
                #     )

            n_aneks += 1

            print(f'Handled {n_aneks} aneks')

        elapsed = time() - start
        print(f'Handled {n_aneks} aneks in {elapsed:.5f} seconds ({elapsed / n_aneks:.5f} seconds per anek in average)')


@main.command()
@argument('anecdotes', type = str)
@argument('speech-path', type = str)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = Crt.name)
@option('--offset', '-o', help = 'number of entries to skip', type = int, default = None)
@option('--cloud-root', '-c', help = 'root folder at the mail.ru cloud - if this option is set, the command works in upload-only mode meaning that existing files are just uploaded to the cloud')
@option('--username', '-u', help = 'username for updating files in the cloud')
@option('--password', '-p', help = 'password for updating files in the cloud')
def uncensor(anecdotes: str, speech_path: str, engine: str, offset: int, cloud_root: str, username: str, password: str):
    cm = None if cloud_root is None else CloudMail(username, password)

    index = SpeechIndex(speech_path)
    ph = ProfanityHandler()

    speaker = RaconteurFactory().make(engine, max_n_characters = 300) if cloud_root is None else None

    df = read_csv(anecdotes, sep = '\t')

    n_rows, _ = df.shape
    pbar = tqdm(total = n_rows, desc = 'Handling documents', initial = 0 if offset is None else offset)

    df = df if offset is None else df.iloc[offset:, ]

    n_spoken = 0

    for i, row in df.iterrows():
        text, changed, _ = ph.uncensor(row['text'])

        if changed:
            if cloud_root is None:
                try:
                    speaker.speak(
                        text = text,
                        filename = index.get(row['source'], row['id']).path
                    )

                    n_spoken += 1
                    pbar.desc = f'Handling documents (spoken: {n_spoken})'
                except Exception:
                    print('Failed to complete the operation, continue from', i)
                    raise
            else:
                location = index.get(row['source'], row['id'])

                # remote_path = f'{cloud_root}/{location.file}'.replace('.mp3', ' (1).mp3')
                remote_path = f'{cloud_root}/{location.file}'

                response = cm.api.file.remove(remote_path)

                # if response['status'] == 200:
                #     print(remote_path)

                if response['status'] != 200:
                    raise ValueError(f'Cannot remove file {location.file}')

                response = cm.api.file.add(location.path, remote_path)

                if response['status'] != 200:
                    raise ValueError(f'Cannot upload file {location.file}')

                print(f'Uploaded file {location.file}')

            # print('=' * 10)
            # print(row['text'])
            # print('-' * 10)
            # print(text)
            # print('*' * 10)
            # print(index.get(row['source'], row['id']))

        pbar.update()


if __name__ == '__main__':
    main()
