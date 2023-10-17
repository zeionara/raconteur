import torch

from .Raconteur import Raconteur

REPO = 'snakers4/silero-models'
MODEL = 'silero_tts'


class Silero(Raconteur):
    name = 'silero'

    def __init__(self, model: str = 'v4', gpu: bool = True, artist: str = 'xenia', ru: bool = True, *args, **kwargs):
        self.model = model
        self.artist = artist

        self.language = 'ru' if ru else 'en'

        self.device = torch.device('cuda' if gpu else 'cpu')

        # model, _ = torch.hub.load(
        #     repo_or_dir = REPO,
        #     model = MODEL,
        #     language = 'ru' if ru else 'en',
        #     speaker = f'{model}_{language}'
        # )

        # self.model = model

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        # data = self.model.apply_tts(
        #     text = text,
        #     speaker = self.artist,
        #     sample_rate = self.sample_rate
        # )
        model, _ = torch.hub.load(
            repo_or_dir = REPO,
            model = MODEL,
            language = self.language,
            speaker = f'{self.model}_{self.language}'
        )

        model.to(self.device)

        data = model.apply_tts(
            text = text,
            speaker = self.artist,
            sample_rate = self.sample_rate
        )

        return data.numpy()

    @property
    def sample_rate(self):
        return 48_000

    @property
    def dtype(self):
        return 'float32'

    def set_file_meta(self, file):
        file['artist'] = self.artist
