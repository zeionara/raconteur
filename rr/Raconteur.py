import os
from abc import ABC, abstractmethod
from uuid import uuid4
from traceback import format_exc

from scipy.io.wavfile import write as write_wav
import numpy as np
from IPython.display import Audio
from pydub import AudioSegment
from music_tag import load_file
from tqdm import tqdm

from .Splitter import Splitter
from .util import drop_empty_lines  # , drop_accent_marks


class Raconteur(ABC):
    name = None

    def __init__(self, splitter: Splitter, tmp_filename: str = None):
        if tmp_filename is None:
            self.tmp_filename = os.path.join(os.sep, 'tmp', f'{str(uuid4())}.wav')

        self.splitter = splitter

    def speak(
        self, text: str, filename: str = None, pbar: bool = False, save_text: str = True, accumulator = None,
        batch_size: int = None, first_batch_index: int = 0, title: str = None, update: bool = True
    ):
        audio = self._say(text, pbar = pbar, accumulator = accumulator, batch_size = batch_size, path_template = filename, first_batch_index = first_batch_index, title = title, update = update)

        if accumulator is None and audio is not None:
            self.save(audio, filename, text if save_text else None)

        return audio

    def save(self, audio: np.array, filename: str, text: str = None, title: str = None):
        # print(audio.dtype)
        # normalized_audio = audio / np.max(np.abs(audio))
        # normalized_audio = (normalized_audio * 32767).astype(np.int16)

        # AudioSegment(normalized_audio.tobytes(), frame_rate = self.sample_rate, sample_width = 2, channels = 1).export(filename, format = 'mp3')
        AudioSegment(self.to_int16(audio).tobytes(), frame_rate = self.sample_rate, sample_width = 2, channels = 1).export(filename, format = 'mp3')
        # AudioSegment.from_numpy(audio, frame_rate = self.sample_rate, channels = 1).export(filename, format = 'mp3')

        # write_wav(
        #     self.tmp_filename,
        #     self.sample_rate,
        #     audio
        # )

        # AudioSegment.from_wav(self.tmp_filename).export(filename, format = 'mp3')

        # os.remove(self.tmp_filename)

        self.update(filename, text, title)

        return None if audio.size < 1 else Audio(audio, rate = self.sample_rate)

    def update(self, filename: str, text: str = None, title: str = None):
        file = load_file(filename)

        if text is not None:
            file['title'] = text if title is None else title
            file['lyrics'] = text
            file['comment'] = text

            if title is not None:
                file['album'] = title[::-1].split('-', maxsplit = 1)[1][::-1]
            # file['year'] = 2023

        self.set_file_meta(file)

        file.save()

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

    def preprocess(self, text: str):
        return text

    def to_int16(self, data):
        raise NotImplementedError()

    def _say(
        self, text: str, pbar: bool = False, accumulator = None, batch_size: int = None, path_template: str = None, first_batch_index: int = 0, title: str = None,
        update: bool = True
    ):
        if batch_size is None:
            combined = np.array([], dtype = self.dtype) if accumulator is None else accumulator

            items = self.splitter.split(self.preprocess(text))
            chunks = tqdm(items) if pbar else items

            for chunk in chunks:
                # print(text)
                # print(chunk, len(chunk))

                try:
                    predictions = self.predict(chunk)
                # except ValueError:
                except (OSError, KeyboardInterrupt):
                    raise
                except:
                    print(format_exc())
                    print(f'Cannot generate speech for text "{chunk}". Setting predictions to an empty array')
                    predictions = np.array([], dtype = self.dtype)

                combined = np.concatenate((combined, predictions))

            return combined

        assert accumulator is None, 'Accumulator must be none in a multibatch setting'
        assert path_template is not None, 'Path template is required in a multibatch setting'
        assert title is not None, 'Title template is required in a multibatch setting'

        combined = np.array([], dtype = self.dtype)

        items = self.splitter.split(text)
        chunks = tqdm(items) if pbar else items

        batch_length = 0
        batch_index = first_batch_index
        text = ''
        path = path_template.format(batch = batch_index)

        def save():
            nonlocal batch_length, combined, batch_index, text, path

            if update:
                self.update(path, drop_empty_lines(text), title = title.format(batch = batch_index))
                # self.update(path_template.format(batch = batch_index), drop_empty_lines(drop_accent_marks(text)), title.format(batch = batch_index))
                # self.update(path_template.format(batch = batch_index), drop_empty_lines(drop_accent_marks(text)), f'{batch_index:02d}')
            elif not os.path.isfile(path):
                # self.save(combined, path_template.format(batch = batch_index), drop_empty_lines(drop_accent_marks(text)), title = title.format(batch = batch_index))
                self.save(combined, path, drop_empty_lines(text), title = title.format(batch = batch_index))

            batch_length = 0
            combined = np.array([], dtype = self.dtype)
            batch_index += 1
            text = ''
            path = path_template.format(batch = batch_index)

        for chunk in chunks:
            # print(text)
            # print(chunk, len(chunk))

            text = f'{text} {chunk}'
            if not update and not os.path.isfile(path):
                combined = np.concatenate((combined, self.predict(chunk)))

            batch_length += len(chunk)

            if batch_length >= batch_size:
                save()

        if combined.shape[0] > 0 or update and os.path.isfile(path_template.format(batch = batch_index)):
            save()

        return None
