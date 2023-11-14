from os import path, remove

import numpy as np
from tqdm import tqdm

from .RaconteurFactory import RaconteurFactory


def _alternate(text: str, artist_one: str, artist_two: str, output_path: str = None, quiet: bool = False):
    assert artist_one != artist_two, 'The two artist must not be same'

    if output_path is None:
        output_path = f'{path.splitext(text)[0]}.mp3'

    factory = RaconteurFactory(gpu = True, ru = True)

    a1 = factory.make(engine = 'silero', artist = artist_one)
    a2 = factory.make(engine = 'silero', artist = artist_two)

    a1_speaks = True

    accumulator = np.array([], dtype = 'float32')

    with open(text, 'r', encoding = 'utf-8') as file:
        lines = file.read().split('\n')

    pbar = None if quiet else tqdm(total = len(lines))

    for line in lines:
        if line:
            # You can't create two objects for the artist and reuse them - in this case the program hangs after the first iteration
            accumulator = (a1 if a1_speaks else a2).speak(line, save_text = False, accumulator = accumulator)
            a1_speaks = not a1_speaks

        if not quiet:
            pbar.update()

    try:
        a1.save(accumulator, filename = output_path)
    except ValueError:
        print(f'Can\'t save file {output_path}')
        raise


# def _alternate_pool_wrapper(args: [str], artist_one: str, artist_two: str, pbar, lock: Lock):
def _alternate_pool_wrapper(args: [str], artist_one: str, artist_two: str):
    _alternate(args[0], artist_one, artist_two, args[1], quiet = True)

    print('+1')
    remove(args[0]) # delete txt file with source text

    # with lock:
    #     pbar.update()
