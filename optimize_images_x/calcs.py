from functools import lru_cache

from optimize_images.data_structures import TaskResult


@lru_cache(maxsize=10)
def get_percent_str(percent_saved: float) -> str:
    return '--' if percent_saved == 0 else f'{percent_saved:.1f}'


def calc_percent_saved(result: TaskResult) -> float:
    percent_saved = ((result.orig_size - result.final_size) / result.orig_size)
    return percent_saved * 100


@lru_cache(maxsize=10)
def to_kilobytes(number: int):
    return f'{(number / 1024.0):.1f}'


@lru_cache(maxsize=10)
def human(number: int, suffix: str = 'B', divisor: float = 1000.0) -> str:
    """Return a human readable memory size in a string.
    Initially written by Fred Cirera, modified and shared by Sridhar Ratnakumar
    (https://stackoverflow.com/a/1094933/6167478), edited by Victor Domingos.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(number) < divisor:
            return f"{number:3.1f} {unit}{suffix}"
        number = number / divisor
    return f"{number:.1f}{'Yi'}{suffix}"
