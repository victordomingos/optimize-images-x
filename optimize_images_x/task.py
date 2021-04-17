import os
from dataclasses import dataclass

from optimize_images_x.calcs import human


@dataclass
class Task:
    filepath: str
    status: int
    original_filesize: int = 0
    final_filesize: int = 0

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def orig_file_size_h(self) -> str:
        return human(self.original_filesize)

    @property
    def final_file_size_h(self) -> str:
        if self.final_filesize != 0:
            return human(self.final_filesize)
        else:
            return ''

    @property
    def bytes_saved(self) -> int:
        if self.final_filesize == 0:
            return 0
        elif self.final_filesize == self.original_filesize:
            return 0
        else:
            return self.original_filesize - self.final_filesize

    @property
    def percent_saved(self) -> float:
        if self.bytes_saved == 0:
            return 0.0

        return self.bytes_saved / self.original_filesize * 100
