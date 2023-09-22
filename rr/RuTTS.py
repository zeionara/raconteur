from RUTTS import TTS
from ruaccent import RUAccent

from .Raconteur import Raconteur


RUTTS_MODEL_PATH = './assets/rutts'
ACCENTIZER_MODEL_PATH = './assets/accentizer'


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

    def predict(self, text):
        return self.tts(
            self.accentizer.process_all(text),
            lenght_scale = self.length_scale
        )

    def set_file_meta(self, file):
        file['artist'] = self.artist
