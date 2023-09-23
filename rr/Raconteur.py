from abc import ABC, abstractmethod

from scipy.io.wavfile import write as write_wav
import numpy as np
from IPython.display import Audio
from pydub import AudioSegment
from music_tag import load_file

from .Splitter import Splitter


class Raconteur(ABC):
    def __init__(self, splitter: Splitter, tmp_filename: str = "/tmp/audio.wav"):
        self.tmp_filename = tmp_filename
        self.splitter = splitter

    def speak(self, text: str, filename: str):
        write_wav(
            self.tmp_filename,
            self.sample_rate,
            # audio := generate_audio(row['text'], history_prompt = ARTIST)
            audio := self._say(text)
        )

        AudioSegment.from_wav(self.tmp_filename).export(filename, format = 'mp3')

        file = load_file(filename)

        file['title'] = text
        file['lyrics'] = text
        file['comment'] = text

        self.set_file_meta(file)

        file.save()

        return Audio(audio, rate = self.sample_rate)

    @property
    @abstractmethod
    def sample_rate(self):
        pass

    @property
    @abstractmethod
    def dtype(self):
        pass

    @abstractmethod
    def predict(self, text):
        pass

    def set_file_meta(self, file):
        pass

    def _say(self, text: str):
        combined = np.array([], dtype = self.dtype)

        for chunk in self.splitter.split(text):
            combined = np.concatenate((combined, self.predict(chunk)))

        return combined
