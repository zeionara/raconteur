import os
from abc import ABC, abstractmethod

from scipy.io.wavfile import write as write_wav
import numpy as np
from IPython.display import Audio
from pydub import AudioSegment
from music_tag import load_file
from tqdm import tqdm

from .Splitter import Splitter


class Raconteur(ABC):
    name = None

    def __init__(self, splitter: Splitter, tmp_filename: str = "/tmp/audio.wav"):
        self.tmp_filename = tmp_filename
        self.splitter = splitter

    def speak(self, text: str, filename: str = None, pbar: bool = False, save_text: str = True, accumulator = None):
        audio = self._say(text, pbar = pbar, accumulator = accumulator)

        if accumulator is None:
            self.save(audio, filename, text if save_text else None)

        return audio

    def save(self, audio: np.array, filename: str, text: str = None):
        write_wav(
            self.tmp_filename,
            self.sample_rate,
            audio
        )

        AudioSegment.from_wav(self.tmp_filename).export(filename, format = 'mp3')

        file = load_file(filename)

        if text is not None:
            file['title'] = text
            file['lyrics'] = text
            file['comment'] = text

        self.set_file_meta(file)

        file.save()

        os.remove(self.tmp_filename)

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

    def _say(self, text: str, pbar: bool = False, accumulator = None):
        combined = np.array([], dtype = self.dtype) if accumulator is None else accumulator

        items = self.splitter.split(text)
        chunks = tqdm(items) if pbar else items

        for chunk in chunks:
            # print(text)
            # print(chunk, len(chunk))

            combined = np.concatenate((combined, self.predict(chunk)))

        return combined
