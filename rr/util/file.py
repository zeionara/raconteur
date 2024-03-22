from time import sleep
from pathlib import Path


IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
VIDEO_EXTENSIONS = ('.mp4', '.webm')


def read(path: str):
    with open(path, 'r', encoding = 'utf-8') as file:
        return file.read()


def is_audio(path: str):
    return path.endswith('mp3')


def is_image(path: str):
    return Path(path).suffix in IMAGE_EXTENSIONS


def is_video(path: str):
    return Path(path).suffix in VIDEO_EXTENSIONS


def is_url(path: str):
    return path.startswith('http')
