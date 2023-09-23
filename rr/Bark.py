from bark import SAMPLE_RATE, generate_audio

from .Raconteur import Raconteur


class Bark(Raconteur):
    def __init__(self, artist: str, *args, **kwargs):
        self.artist = artist
        super().__init__(*args, **kwargs)

    @property
    def sample_rate(self):
        return SAMPLE_RATE

    @property
    def dtype(self):
        return 'float32'

    def predict(self, text):
        return generate_audio(text, history_prompt = self.artist)

    def set_file_meta(self, file):
        file['artist'] = self.artist
