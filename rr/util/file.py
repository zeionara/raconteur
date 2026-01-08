from aiohttp import ClientTimeout, ClientSession
from io import BytesIO
from time import sleep
from pathlib import Path


IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
VIDEO_EXTENSIONS = ('.mp4', '.webm')

TIMEOUT = 300  # 5 minutes


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


async def fetch_file_async(url: str):
    timeout = ClientTimeout(total=TIMEOUT)

    async with ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()

    return BytesIO(content)
