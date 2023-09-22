from click import group, argument, option

from .Splitter import Splitter

from .Bark import Bark
from .RuTTS import RuTTS

from RUTTS import TTS
from ruaccent import RUAccent


@group()
def main():
    pass


@main.command()
@argument('text', type = str)
@option('--max-n-characters', '-c', help = 'max number of characters given to the speech engine at once', type = int, default = None)
def say(text: str, max_n_characters: int):

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
    RuTTS(splitter = Splitter(max_n_characters), add_time_to_end = 0.1, length_scale = 1.65).speak(text, filename = 'assets/speech.mp3')

    # splitter = Splitter(max_n_characters)

    # print(splitter.split(text))


if __name__ == '__main__':
    main()
