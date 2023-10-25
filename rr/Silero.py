import torch

from transliterate import translit
# from ruaccent import RUAccent

from .Raconteur import Raconteur
from .util import translate_numbers
# from .RuTTS import ACCENTIZER_MODEL_PATH

REPO = 'snakers4/silero-models'
MODEL = 'silero_tts'

DOUBLE_LINE_BREAK = '\n\n'
PAUSE = '\n<break time="2000ms"/>\n'

PRE_PARAGRAPH_PAUSE_LENGTH = 50_000
POST_PARAGRAPH_PAUSE_LENGTH = 50_000


class Silero(Raconteur):
    name = 'silero'

    def __init__(self, model: str = 'v4', gpu: bool = True, artist: str = 'xenia', ru: bool = True, ssml: bool = False, *args, **kwargs):
        self.model = model
        self.artist = artist

        self.language = 'ru' if ru else 'en'

        self.device = torch.device('cuda' if gpu else 'cpu')
        self.ssml = ssml

        # self.accentizer = accentizer = RUAccent(workdir = ACCENTIZER_MODEL_PATH)
        # accentizer.load()

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

        text = translate_numbers(translit(text, 'ru') if self.language == 'ru' else text, lang = self.language)

        if ssml := self.ssml:
            # text_with_tags = self.accentizer.process_all(text)
            # print(text_with_tags)
            # text_with_tags = f'<speak>\n<p>\n{text_with_tags.replace(DOUBLE_LINE_BREAK, PAUSE)}\n</p>\n</speak>'
            text_with_tags = f'<speak>\n<p>\n{text.replace(DOUBLE_LINE_BREAK, PAUSE)}\n</p>\n</speak>'
            text_with_tags = text_with_tags.replace('»', '"').replace('«', '"').replace('&', 'энд')
        else:
            text_with_tags = None

        # if self.ssml:
        #     print(text_with_tags)

        try:
            data = model.apply_tts(
                text = None if ssml else text,
                ssml_text = text_with_tags if ssml else None,
                # text = text,
                speaker = self.artist,
                sample_rate = self.sample_rate,
                put_accent = True,
                put_yo = True
            )
        except Exception:
            print('Text: ', text_with_tags if self.ssml else text)
            raise

        vector = data.numpy()

        if ssml:
            return vector[PRE_PARAGRAPH_PAUSE_LENGTH:-POST_PARAGRAPH_PAUSE_LENGTH]  # cut the pause in the beginning and at the end of paragraph

        return vector

    @property
    def sample_rate(self):
        return 48_000

    @property
    def dtype(self):
        return 'float32'

    def set_file_meta(self, file):
        file['artist'] = self.artist
