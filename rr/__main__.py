from os import path, makedirs
from time import time

from click import group, argument, option
from pandas import read_csv

from .Splitter import Splitter
from .RuTTS import RuTTS


@group()
def main():
    pass


@main.command()
@argument('text', type = str)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
def say(text: str, max_n_characters: int, gpu: bool):

    # tts = TTS("TeraTTS/natasha-g2p-vits", add_time_to_end=0.8)
    # # tts = TTS('TeraTTS/natasha-g2p-vits', add_time_to_end = 0.8)

    # accentizer = RUAccent(workdir = './assets/accentizer')

    # accentizer.load(omograph_model_size = 'medium')

    # text = accentizer.process_all(text)

    # audio = tts(text, length_scale = 1.65)

    # tts.save_wav(audio, './audio.wav')

    # print(audio)

    # # print(text)

    # Bark(artist = 'v2/ru_speaker_6', splitter = Splitter(max_n_characters)).speak(text, filename = 'assets/speech.mp3')
    RuTTS(splitter = Splitter(max_n_characters), add_time_to_end = 0.1, length_scale = 1.65, gpu = gpu).speak(text, filename = 'assets/speech.mp3')

    # splitter = Splitter(max_n_characters)

    # print(splitter.split(text))


@main.command()
@option('--source', '-s', help = 'path to the input tsv file with anecdotes', type = str, default = 'assets/anecdotes.tsv')
@option('--destination', '-d', help = 'path to the output directory with anecdotes', type = str, default = 'assets/anecdotes')
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
@option('--top-n', '-n', help = 'number of entries to handle', type = int, default = None)
@option('--offset', '-o', help = 'number of entries in the beginning to skip', type = int, default = None)
@option('--gpu', '-g', help = 'run model using gpu', is_flag = True)
def handle_aneks(source: str, destination: str, max_n_characters: int, top_n: int, offset: int, gpu: bool):
    if not path.isdir(destination):
        makedirs(destination)

    df = read_csv(source, sep = '\t')

    n_aneks = 0

    # speaker = Bark(artist = 'v2/ru_speaker_6', splitter = Splitter(max_n_characters = 200))
    speaker = RuTTS(splitter = Splitter(max_n_characters), add_time_to_end = 0.1, length_scale = 1.65, gpu = gpu)

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
