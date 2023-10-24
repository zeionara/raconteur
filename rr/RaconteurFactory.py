from os import environ as env

from .Splitter import Splitter

from .Bark import Bark
from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech
from .Crt import Crt
from .Coqui import Coqui
from .Silero import Silero


class RaconteurFactory:
    def __init__(self, gpu: bool = False, ru: bool = False):
        self.gpu = gpu
        self.ru = ru

    def make(self, engine: str, max_n_characters: int = None, artist: str = None, ssml: bool = False):
        match engine:
            case SaluteSpeech.name:
                return SaluteSpeech(
                    # client_id = env['SALUTE_SPEECH_CLIENT_ID'],
                    # client_secret = env['SALUTE_SPEECH_CLIENT_SECRET'],
                    auth = env['SALUTE_SPEECH_AUTH'],
                    artist = 'Nec',
                    splitter = Splitter(4000 if max_n_characters is None else max_n_characters)
                )
            case Bark.name:
                return Bark(
                    artist = 'v2/ru_speaker_6' if self.ru else 'v2/en_speaker_6',
                    splitter = Splitter(200 if max_n_characters is None else max_n_characters)
                )
            case RuTTS.name:
                return RuTTS(
                    artist = 'TeraTTS/natasha-g2p-vits',
                    splitter = Splitter(1000 if max_n_characters is None else max_n_characters),
                    add_time_to_end = 0.1,
                    length_scale = 1.65,
                    gpu = self.gpu
                )
            case Crt.name:
                return Crt(
                    username = env['CRT_USERNAME'],
                    password = env['CRT_PASSWORD'],
                    domain = int(env['CRT_DOMAIN']),
                    artist = 'Vladimir_n',
                    splitter = Splitter(500 if max_n_characters is None else max_n_characters)
                )
            case Coqui.name:
                return Coqui(
                    speaker_wav = 'assets/female.wav',
                    gpu = self.gpu,
                    ru = self.ru,
                    splitter = Splitter(200 if max_n_characters is None else max_n_characters)
                )
            case Silero.name:
                return Silero(
                    model = 'v4' if self.ru else 'v3',
                    gpu = self.gpu,
                    artist = ('xenia' if self.ru else 'en_1') if artist is None else artist,
                    ru = self.ru,
                    splitter = Splitter(400 if max_n_characters is None else max_n_characters),
                    ssml = ssml
                )
            case _:
                raise ValueError(f'Unknown engine {engine}')
