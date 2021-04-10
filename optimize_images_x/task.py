import os
from dataclasses import dataclass

from optimize_images_x.file_utils import to_kilobytes


@dataclass
class Task:
    filepath: str
    status: str
    original_filesize: int = 0
    final_filesize: int = 0

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def orig_file_size_h(self) -> str:
        return to_kilobytes(self.original_filesize)
        # return human(self.original_filesize)

    @property
    def bytes_saved(self) -> int:
        return self.final_filesize - self.original_filesize

    @property
    def percent_saved(self) -> float:
        return self.bytes_saved / self.original_filesize
