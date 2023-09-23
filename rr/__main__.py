from os import path, makedirs, environ as env
from time import time

from click import group, argument, option, Choice
from pandas import read_csv

from .Splitter import Splitter
from .Bark import Bark
from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech

from .RaconteurFactory import RaconteurFactory


ENGINES = Choice((Bark.name, RuTTS.name, SaluteSpeech.name), case_sensitive = False)


@group()
def main():
    pass


@main.command()
@argument('text', type = str)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = RuTTS.name)
@option('--destination', '-d', help = 'path to the resulting mp3 file', type = str, default = 'assets/speech.mp3')
def say(text: str, max_n_characters: int, gpu: bool, engine: str, destination: str):
    RaconteurFactory(gpu).make(engine, max_n_characters).speak(text, filename = destination)


@main.command()
@option('--source', '-s', help = 'path to the input tsv file with anecdotes', type = str, default = 'assets/anecdotes.tsv')
@option('--destination', '-d', help = 'path to the output directory with anecdotes', type = str, default = 'assets/anecdotes')
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--top-n', '-n', help = 'number of entries to handle', type = int, default = None)
@option('--offset', '-o', help = 'number of entries in the beginning to skip', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
@option('--engine', '-e', help = 'speaker type to use', type = ENGINES, default = RuTTS.name)
def handle_aneks(source: str, destination: str, max_n_characters: int, top_n: int, offset: int, gpu: bool, engine: str):
    if not path.isdir(destination):
        makedirs(destination)

    df = read_csv(source, sep = '\t')

    n_aneks = 0

    speaker = RaconteurFactory(gpu).make(engine, max_n_characters)

    start = time()

    for _, row in (
        (
            df if offset is None else df.iloc[offset:,]
        )
        if top_n is None else
        (
            df.iloc[:top_n,] if offset is None else df.iloc[offset:top_n,]
        )
    ).loc[:, ('id', 'text')].iterrows():
        text = row['text']

        speaker.speak(
            text = text,
            filename = path.join(destination, f'{row["id"]:08d}.mp3')
        )

        n_aneks += 1

        print(f'Handled {n_aneks} aneks')

    elapsed = time() - start
    print(f'Handled {n_aneks} aneks in {elapsed:.5f} seconds ({elapsed / n_aneks:.5f} seconds per anek in average)')


if __name__ == '__main__':
    main()
