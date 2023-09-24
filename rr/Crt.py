import base64
from uuid import uuid4
from io import BytesIO

from requests import post
from scipy.io.wavfile import read as read_wav

from .Raconteur import Raconteur


SESSION_MANAGEMENT_URL = 'https://cloud.speechpro.com/vksession/rest/session'
SYNTHESIS_URL = 'https://cloud.speechpro.com/vktts/rest/v1/synthesize'

TIMEOUT = 100


class Crt(Raconteur):
    name = 'crt'

    def __init__(self, username: str, password: str, domain: int, artist: str, *args, **kwargs):
        self.username = username
        self.password = password
        self.domain = domain

        self.artist = artist

        self.session_id = None

        super().__init__(*args, **kwargs)

    def predict(self, text: str):
        if self.session_id is None:
            self._create_session()

        response = post(
            SYNTHESIS_URL,
            headers = {
                'X-Session-ID': self.session_id,
                'X-Request-Id': str(uuid4())
            },
            json = {
                'voice_name': self.artist,
                'text': {
                    'mime': 'text/plain',
                    'value': text
                },
                'audio': 'audio/wav'
            },
            timeout = TIMEOUT
        )

        data = response.json().get('data')

        if data is None:
            raise KeyError(f'No "data" field in response from crt service: {response.text}. Probably, the quota has been exhausted')

        _, data = read_wav(
            BytesIO(
                base64.decodebytes(
                    bytes(
                        data,
                        'utf-8'
                    )
                )
            )
        )

        return data

    @property
    def sample_rate(self):
        return 22_050

    @property
    def dtype(self):
        return 'int16'

    def _create_session(self):

        response = post(
            SESSION_MANAGEMENT_URL,
            json = {
                'username': self.username,
                'password': self.password,
                'domain_id': self.domain
            },
            timeout = TIMEOUT
        )

        self.session_id = response.json()['session_id']

    def set_file_meta(self, file):
        file['artist'] = self.artist
