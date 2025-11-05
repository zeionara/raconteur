from requests import post
from uuid import uuid4
from datetime import datetime
from io import BytesIO

from scipy.io.wavfile import read as read_wav

from .Raconteur import Raconteur


OAUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
TTS_URL = 'https://smartspeech.sber.ru/rest/v1/text:synthesize'

TIMEOUT = 100


class SaluteSpeech(Raconteur):
    name = 'salute'

    # def __init__(self, client_id: str, client_secret: str, auth: str, artist = 'Nec', *args, **kwargs):
    def __init__(self, auth: str, artist = 'Nec', *args, **kwargs):
        # self.client_id = client_id
        # self.client_secret = client_secret
        self.auth = auth
        self.artist = artist

        self.access_token = None
        self.access_token_expires = None

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        if self.access_token is None or datetime.now() > self.access_token_expires:
            self._refresh_access_token()

        response = post(
            TTS_URL,
            data = text.encode('utf-8'),
            params = {
                'format': 'wav16',
                'voice': f'{self.artist}_{self.sample_rate}'
            },
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/text'
            },
            verify = False,
            timeout = TIMEOUT
        )

        _, data = read_wav(BytesIO(response.content))

        # with open('audio.wav', 'wb') as file:
        #     file.write(response.content)

        # _, data = read_wav('audio.wav')
        # print(data.dtype)

        # write_wav('audioo.wav', self.sample_rate, data)

        return data

        # print(data)

    def _refresh_access_token(self):
        response = post(
            OAUTH_URL,
            data = {
                'scope': 'SALUTE_SPEECH_PERS'
            },
            headers = {
                'Authorization': f'Basic {self.auth}',
                'RqUID': str(uuid4())
            },
            verify = False,
            timeout = TIMEOUT
        ).json()

        self.access_token = response['access_token']
        self.access_token_expires = datetime.fromtimestamp(response['expires_at'] / 1000)

    @property
    def sample_rate(self):
        return 24_000

    @property
    def dtype(self):
        return 'int16'

    def set_file_meta(self, file):
        file['artist'] = self.artist

    def to_int16(self, data):
        return data
