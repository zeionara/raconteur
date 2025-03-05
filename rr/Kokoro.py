from numpy import float32, int16, max as np_max, abs as np_abs

from torch import cat
from kokoro import KPipeline

from .Raconteur import Raconteur

REPO = 'snakers4/silero-models'
MODEL = 'silero_tts'

DOUBLE_LINE_BREAK = '\n\n'
PAUSE = '\n<break time="2000ms"/>\n'

PRE_PARAGRAPH_PAUSE_LENGTH = 50_000
POST_PARAGRAPH_PAUSE_LENGTH = 50_000


class Kokoro(Raconteur):
    name = 'kokoro'

    # def __init__(self, *args, repo_id: str = 'hexgrad/Kokoro-82M-v1.1-zh', gpu: bool = True, artist: str = 'heart', gender: str = 'f', lang_code: str = 'a', speed: float = 1., **kwargs):
    def __init__(self, *args, repo_id: str = 'hexgrad/Kokoro-82M', gpu: bool = True, artist: str = 'heart', gender: str = 'f', lang_code: str = 'a', speed: float = 1., **kwargs):
        self.device = 'cuda' if gpu else 'cpu'
        self.artist = artist.capitalize()
        self.gender = gender
        self.lang_code = lang_code
        self.speed = speed

        self.speaker = f'{self.lang_code}{self.gender}_{self.artist}'.lower()

        self.pipeline = KPipeline(repo_id = repo_id, lang_code = lang_code, device = 'cuda' if gpu else 'cpu')

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        try:
            audios = []
            for _, _, audio in self.pipeline(text, voice = self.speaker, speed = self.speed):
                audios.append(audio)
                # samples = audio.shape[0] if audio is not None else 0
                # assert samples > 0, "No audio generated"
                # return samples
        except Exception:
            print('Text: ', text)
            raise

        return cat(audios).numpy()

        # vector = samples.numpy()

        # return vector

    @property
    def sample_rate(self):
        return 24_000

    @property
    def dtype(self):
        return 'float32'

    def to_int16(self, data: float32):
        return (data / np_max(np_abs(data)) * 32767).astype(int16)

    def set_file_meta(self, file):
        file['artist'] = self.artist
