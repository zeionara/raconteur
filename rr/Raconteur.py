import os
from abc import ABC, abstractmethod
from uuid import uuid4

from scipy.io.wavfile import write as write_wav
import numpy as np
from IPython.display import Audio
from pydub import AudioSegment
from music_tag import load_file
from tqdm import tqdm

from .Splitter import Splitter


class Raconteur(ABC):
    name = None

    def __init__(self, splitter: Splitter, tmp_filename: str = None):
        if tmp_filename is None:
            self.tmp_filename = os.path.join(os.sep, 'tmp', f'{str(uuid4())}.wav')

        self.splitter = splitter

    def speak(self, text: str, filename: str = None, pbar: bool = False, save_text: str = True, accumulator = None, batch_size: int = None):
        audio = self._say(text, pbar = pbar, accumulator = accumulator, batch_size = batch_size, path_template = filename)

        if accumulator is None and audio is not None:
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

    def _say(self, text: str, pbar: bool = False, accumulator = None, batch_size: int = None, path_template: str = None):
        if batch_size is None:
            combined = np.array([], dtype = self.dtype) if accumulator is None else accumulator

            items = self.splitter.split(text)
            chunks = tqdm(items) if pbar else items

            for chunk in chunks:
                # print(text)
                # print(chunk, len(chunk))

                combined = np.concatenate((combined, self.predict(chunk)))

            return combined
        else:
            assert accumulator is None, 'Accumulator must be none in a multibatch setting'
            assert path_template is not None, 'Path template is required in a multibatch setting'

            combined = np.array([], dtype = self.dtype)

            items = self.splitter.split(text)
            chunks = tqdm(items) if pbar else items

            batch_length = 0
            batch_index = 0

            def save():
                nonlocal batch_length, combined, batch_index

                self.save(combined, path_template.format(batch = batch_index), text = f'{batch_index:02d}')

                batch_length = 0
                combined = np.array([], dtype = self.dtype)
                batch_index += 1

            for chunk in chunks:
                # print(text)
                # print(chunk, len(chunk))

                combined = np.concatenate((combined, self.predict(chunk)))

                batch_length += len(chunk)

                if batch_length >= batch_size:
                    save()

            if combined.shape[0] > 0:
                save()

            return None
