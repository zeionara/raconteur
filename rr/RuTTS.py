import re

from RUTTS import TTS
from ruaccent import RUAccent
from transliterate import translit
# from num2words import num2words
# from onnxruntime.capi.onnxruntime_pybind11_state import RuntimeException

from .Raconteur import Raconteur

from .util import translate_numbers


RUTTS_MODEL_PATH = './assets/rutts'
ACCENTIZER_MODEL_PATH = './assets/accentizer'

NUMBER_PATTERN = re.compile('[-+]?[0-9]+')


class RuTTS(Raconteur):
    name = 'rutts'

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

        text = translate_numbers(text)

        # while (match := NUMBER_PATTERN.search(text)) is not None:
        #     number = match.group(0)
        #     text = text.replace(number, num2words(number, lang = 'ru'), 1)

        # Add accent marks

        try:
            text = self.accentizer.process_all(text)
        except Exception:
            print(f'Can\'t put accents in text "{text}"')

        return self.tts(
            text,
            lenght_scale = self.length_scale
        )

    def set_file_meta(self, file):
        file['artist'] = self.artist
