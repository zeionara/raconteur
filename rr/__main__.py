from click import group, argument, option

from .Splitter import Splitter
from .Bark import Bark


@group()
def main():
    pass


@main.command()
@argument('text', type = str)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
def say(text: str, max_n_characters: int):
    Bark(artist = 'v2/ru_speaker_6', splitter = Splitter(max_n_characters)).speak(text, filename = 'assets/speech.mp3')

    # splitter = Splitter(max_n_characters)

    # print(splitter.split(text))


if __name__ == '__main__':
    main()
