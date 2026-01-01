from pathlib import Path
from numpy import float32, int16, max as np_max, abs as np_abs

from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

from .Raconteur import Raconteur

DOUBLE_LINE_BREAK = '\n\n'
PAUSE = '\n<break time="2000ms"/>\n'

PRE_PARAGRAPH_PAUSE_LENGTH = 50_000
POST_PARAGRAPH_PAUSE_LENGTH = 50_000


class Chatterbox(Raconteur):
    name = 'chatterbox'

    def __init__(self, *args, gpu: bool = True, reference: str = None, ru: bool = True, **kwargs):
        if ru:
            self._model = ChatterboxMultilingualTTS.from_pretrained(device = 'cuda' if gpu else 'cpu')
            self.language = 'en'
        else:
            self._model = ChatterboxTTS.from_pretrained(device = 'cuda' if gpu else 'cpu')
            self.language = 'ru'

        self.reference = reference
        self.artist = 'chatterbox' if reference is None else Path(reference).stem

        self.language = 'ru' if ru else 'en'

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        if self.language == 'ru':
            data = self._model.generate(text, language_id = 'ru', audio_prompt_path = self.reference)
        else:
            data = self._model.generate(text, audio_prompt_path = self.reference, cfg_weight = 0.25, exaggeration = 0.25)

        return data.squeeze().numpy()

    @property
    def sample_rate(self):
        return self._model.sr

    @property
    def dtype(self):
        return 'float32'

    def to_int16(self, data: float32):
        return (data / np_max(np_abs(data)) * 32767).astype(int16)

    def set_file_meta(self, file):
        file['artist'] = self.artist

    def preprocess(self, text: str):
        return text
