from enum import Enum
from io import BytesIO
from datetime import datetime

from requests import post
import numpy as np
from scipy.io.wavfile import read as read_wav
from numpy import float32

from .Raconteur import Raconteur
from .GenerationException import GenerationException


OAUTH_URL = 'https://mcs.mail.ru/auth/oauth/v1/token'
TTS_URL = 'https://voice.mcs.mail.ru/tts'

TIMEOUT = 100

HTTP_200_OK = 200


class Model(Enum):
    KATHERINE = 'katherine'
    KATHERINE_HIFIGAN = 'katherine-hifigan'
    MARIA = 'maria'
    MARIA_SERIOUS = 'maria-serious'
    PAVEL = 'pavel'
    PAVEL_HIFIGAN = 'pavel-hifigan'


class Encoder(Enum):
    PCM = 'pcm'
    MP3 = 'mp3'
    OPUS = 'opus'


class VKCloud(Raconteur):
    name = 'vk'

    def __init__(self, client_id: str, client_secret: str, model: Model | None = None, tempo: float | None = None, *args, **kwargs):
        if model is None:
            model = Model.KATHERINE_HIFIGAN

        if tempo is None:
            tempo = 1.0

        assert 0.75 < tempo < 1.75

        self.client_id = client_id
        self.client_secret = client_secret

        self.refresh_token = None
        self.access_token = None
        self.access_token_expires = None

        self.model = model
        self.encoder = Encoder.PCM
        self.tempo = tempo

        super().__init__(*args, **kwargs)

    def _refresh_access_token(self):
        if self.refresh_token is None:
            response = post(
                OAUTH_URL,
                json = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout = TIMEOUT
            )

            if response.status_code != HTTP_200_OK:
                raise GenerationException(f'Unexpected get token response status: {response.status_code} ({response.content})')

            response_json = response.json()

            self.refresh_token = response_json['refresh_token']
            self.access_token = response_json['access_token']
            self.access_token_expires = response_json['expired_in']

            return

        response = post(
            OAUTH_URL,
            json = {
                'client_id': self.client_id,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            },
            timeout = TIMEOUT
        )

        if response.status_code != HTTP_200_OK:
            raise GenerationException(f'Unexpected refresh token response status: {response.status_code} ({response.content})')

        response_json = response.json()

        self.refresh_token = response_json['refresh_token']
        self.access_token = response_json['access_token']
        self.access_token_expires = response_json['expired_in']

    def predict(self, text: str):
        if self.access_token is None or datetime.now() > self.access_token_expires:
            self._refresh_access_token()

        response = post(
            TTS_URL,
            data = text.encode('utf-8'),
            params = {
                'model_name': self.model.value,
                'encoder': self.encoder.value,
                'tempo': self.tempo
            },
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/text'
            },
            # verify = False,
            timeout = TIMEOUT
        )

        if response.status_code != HTTP_200_OK:
            raise GenerationException(f'Unexpected response status: {response.status_code} ({response.content})')

        with open('assets/speech-vk.mp3', 'wb') as file:
            file.write(response.content)

        # _, data = read_wav(BytesIO(response.content))
        data = np.frombuffer(response.content, dtype='>i2').astype(np.int16)

        return data

    @property
    def sample_rate(self):
        return 24_000

    @property
    def dtype(self):
        return 'int16'

    def set_file_meta(self, file):
        file['artist'] = self.model.value

    def to_int16(self, data: float32):
        return data

# class VKCloud(Raconteur):
#     name = 'vk'
#
#     def __init__(self, access_token: str, model: Model | None = None, tempo: float | None = None, *args, **kwargs):
#         if model is None:
#             model = Model.KATHERINE_HIFIGAN
#
#         if tempo is None:
#             tempo = 1.0
#
#         assert 0.75 < tempo < 1.75
#
#         self.access_token = access_token
#         self.model = model
#         self.encoder = Encoder.PCM
#         self.tempo = tempo
#
#         super().__init__(*args, **kwargs)
#
#     def predict(self, text: str):
#         print(f'Bearer {self.access_token}')
#
#         response = post(
#             TTS_URL,
#             data = text.encode('utf-8'),
#             params = {
#                 'model_name': self.model.value,
#                 'encoder': self.encoder.value,
#                 'tempo': self.tempo
#             },
#             headers = {
#                 'Authorization': f'Bearer {self.access_token}',
#                 'Content-Type': 'application/text'
#             },
#             verify = False,
#             timeout = TIMEOUT
#         )
#
#         if response.status_code != HTTP_200_OK:
#             raise GenerationException(f'Unexpected response status: {response.status_code} ({response.content})')
#
#         _, data = read_wav(BytesIO(response.content))
#
#         return data
#
#     @property
#     def sample_rate(self):
#         return 24_000
#
#     @property
#     def dtype(self):
#         return 'int16'
#
#     def set_file_meta(self, file):
#         file['artist'] = self.model.value
#
#     def to_int16(self, data: float32):
#         return data
