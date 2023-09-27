from os import path, makedirs
from time import time

from click import group, argument, option, Choice
from pandas import read_csv

from cloud_mail_api import CloudMail

from .Bark import Bark
from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech
from .Crt import Crt
from .Coqui import Coqui

from .RaconteurFactory import RaconteurFactory

from .util import one_is_not_none, read


ENGINES = Choice((Bark.name, RuTTS.name, SaluteSpeech.name, Crt.name, Coqui.name), case_sensitive = False)


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
def say(text: str, max_n_characters: int, gpu: bool, engine: str, destination: str, russian: bool, txt: str):
    match one_is_not_none('Exactly one of input text, path to txt file must be specified', text, txt):
        case 1:
            text = read(txt)

    # tts = TTS('tts_models/multilingual/multi-dataset/xtts_v1').to('cuda' if gpu else 'cpu')

    # print(tts.tts(
    #     text = text,
    #     speaker_wav = 'assets/female.wav',
    #     language = 'en'
    # ))

    # tts.tts_to_file(
    #     text = text,
    #     file_path = 'audio.wav',
    #     speaker_wav = 'assets/female.wav',
    #     language = 'en'
    # )

    RaconteurFactory(gpu, russian).make(engine, max_n_characters).speak(text, filename = destination)
    # RaconteurFactory(gpu, russian).make('crt', max_n_characters).predict(text)


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
def handle_aneks(
    source: str, destination: str, max_n_characters: int, top_n: int, offset: int, gpu: bool, engine: str, russian: bool, skip_if_exists: bool,
    username: str, password: str, cloud_root: str
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
        filename = path.join(destination, name)

        # print(f'Handling "{text}"')

        if not skip_if_exists or not path.isfile(filename):
            speaker.speak(
                text = text,
                filename = filename
            )

            if cm is not None:
                # print(filename, f'{cloud_root}/{name}')
                cm.api.file.add(filename, f'{cloud_root}/{name}')

        n_aneks += 1

        print(f'Handled {n_aneks} aneks')

    elapsed = time() - start
    print(f'Handled {n_aneks} aneks in {elapsed:.5f} seconds ({elapsed / n_aneks:.5f} seconds per anek in average)')


if __name__ == '__main__':
    main()
