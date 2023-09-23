import numpy as np

from TTS.api import TTS

from .Raconteur import Raconteur


class Coqui(Raconteur):
    name = 'coqui'

    def __init__(self, speaker_wav: str, model: str = 'tts_models/multilingual/multi-dataset/xtts_v1', gpu: bool = True, ru: bool = True, *args, **kwargs):
        self.model = model
        self.gpu = gpu
        self.speaker_wav = speaker_wav
        self.ru = ru

        self.tts = TTS(model).to('cpu')  # to('cuda') causes out of memory error

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        data = self.tts.tts(
            text = text,
            speaker_wav = self.speaker_wav,
            language = 'ru' if self.ru else 'en'
        )

        return np.array(data, dtype = self.dtype)

    @property
    def sample_rate(self):
        return 24_000

    @property
    def dtype(self):
        return 'float32'

    def set_file_meta(self, file):
        file['artist'] = self.speaker_wav
