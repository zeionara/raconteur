import re

from RUTTS import TTS
from ruaccent import RUAccent
from transliterate import translit
from num2words import num2words

from .Raconteur import Raconteur


RUTTS_MODEL_PATH = './assets/rutts'
ACCENTIZER_MODEL_PATH = './assets/accentizer'

NUMBER_PATTERN = re.compile('[-+]?[0-9]+')


class RuTTS(Raconteur):
    def __init__(self, artist: str = 'TeraTTS/natasha-g2p-vits', add_time_to_end = 0.8, length_scale = 1.2, gpu: bool = True, *args, **kwargs):
        self.add_time_to_end = add_time_to_end
        self.length_scale = length_scale
        self.artist = artist

        self.tts = TTS(artist, add_time_to_end = add_time_to_end, save_path = RUTTS_MODEL_PATH, gpu = gpu)
        self.accentizer = accentizer = RUAccent(workdir = ACCENTIZER_MODEL_PATH)
        accentizer.load(omograph_model_size = 'medium')

        super().__init__(*args, **kwargs)

    @property
    def sample_rate(self):
        return 22050

    @property
    def dtype(self):
        return 'float32'

    def predict(self, text):

        # Transliterate

        text = translit(text, 'ru')

        # Replace numbers with words

        while (match := NUMBER_PATTERN.search(text)) is not None:
            number = match.group(0)
            text = text.replace(number, num2words(number, lang = 'ru'), 1)

        return self.tts(
            self.accentizer.process_all(text),
            lenght_scale = self.length_scale
        )

    def set_file_meta(self, file):
        file['artist'] = self.artist
