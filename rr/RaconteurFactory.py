from os import environ as env

from .Splitter import Splitter

from .Bark import Bark
from .RuTTS import RuTTS
from .SaluteSpeech import SaluteSpeech


class RaconteurFactory:
    def __init__(self, gpu: bool = False, ru: bool = False):
        self.gpu = gpu
        self.ru = ru

    def make(self, engine: str, max_n_characters: int):
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
                    artist = 'v2/ru_speaker_6' if self.ru else None,
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
            case _:
                raise ValueError(f'Unknown engine {engine}')
