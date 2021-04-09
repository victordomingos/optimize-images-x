import os
from functools import lru_cache
from typing import Iterable

from optimize_images_x.global_setup import SUPPORTED_FORMATS


@lru_cache(maxsize=10)
def to_kilobytes(number: int):
    return f'{(number / 1024.0):.1f}'


@lru_cache(maxsize=10)
def human(number: int, suffix='B') -> str:
    """Return a human readable memory size in a string.
    Initially written by Fred Cirera, modified and shared by Sridhar Ratnakumar
    (https://stackoverflow.com/a/1094933/6167478), edited by Victor Domingos.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(number) < 1024.0:
            return f"{number:3.1f} {unit}{suffix}"
        number = number / 1024.0
    return f"{number:.1f}{'Yi'}{suffix}"


def search_images(dirpath: str, recursive: bool) -> Iterable[str]:
    if recursive:
        for root, _, files in os.walk(dirpath):
            for filename in files:
                if not os.path.isfile(os.path.join(root, filename)):
                    continue
                extension = os.path.splitext(filename)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.join(root, filename)
    else:
        with os.scandir(dirpath) as directory:
            for dir_entry in directory:
                if not os.path.isfile(os.path.normpath(dir_entry)):
                    continue
                extension = os.path.splitext(dir_entry)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.normpath(dir_entry)
