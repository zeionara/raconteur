from os import path, makedirs
from time import time

from click import group, argument, option, Choice
from pandas import read_csv

from beep import beep
# from cloud_mail_api import CloudMail
from fuck import ProfanityHandler
from tqdm import tqdm
# import torch

from .Bark import Bark
from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech
from .Crt import Crt
from .Coqui import Coqui
from .Silero import Silero

from .RaconteurFactory import RaconteurFactory

from .util import one_is_not_none, read
from .SpeechIndex import SpeechIndex


ENGINES = Choice((Bark.name, RuTTS.name, SaluteSpeech.name, Crt.name, Coqui.name, Silero.name), case_sensitive = False)


@group()
def main():
    pass


@main.command()
@argument('text', type = str, required = False)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = RuTTS.name)
@option('--destination', '-d', help = 'path to the resulting mp3 file', type = str, default = 'assets/speech.mp3')
@option('--russian', '-r', help = 'is input text in russian language', is_flag = True)
@option('--txt', '-t', help = 'read text from a plain .txt file located at the given path', type = str, default = None)
@option('--artist', '-a', help = 'speaker id to use for speech generation', type = str, default = None)
@option('--drop-text', '-x', help = 'do not keep source text in generated audio file metadata (for instance, because the text is very long)', is_flag = True)
def say(text: str, max_n_characters: int, gpu: bool, engine: str, destination: str, russian: bool, txt: str, artist: str, drop_text: bool):

    # language = 'ru'
    # model_id = 'v4_ru'
    # sample_rate = 48_000
    # speaker = 'xenia'

    # device = torch.device('cuda')

    # model, text = torch.hub.load(
    #     repo_or_dir = 'snakers4/silero-models',
    #     model = 'silero_tts',
    #     language = language,
    #     speaker = model_id
    # )

    # model.to(device)

    # audio = model.apply_tts(
    #     text = text,
    #     speaker = speaker,
    #     sample_rate = sample_rate
    # )

    # print(audio.numpy())
    # print(audio.dtype)

    match one_is_not_none('Exactly one of input text, path to txt file must be specified', text, txt):
        case 1:
            text = read(txt)

    RaconteurFactory(gpu, russian).make(engine, max_n_characters, artist).speak(text, filename = destination, pbar = True, save_text = not drop_text)


@main.command()
@option('--source', '-s', help = 'path to the input tsv file with anecdotes', type = str, default = 'assets/anecdotes.tsv')
@option('--destination', '-d', help = 'path to the output directory with anecdotes', type = str, default = 'assets/anecdotes')
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--top-n', '-n', help = 'number of entries to handle', type = int, default = None)
@option('--offset', '-o', help = 'number of entries in the beginning to skip', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = RuTTS.name)
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
