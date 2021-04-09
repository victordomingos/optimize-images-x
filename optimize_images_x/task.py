import os
from dataclasses import dataclass

from optimize_images_x.file_utils import to_kilobytes


@dataclass
class Task:
    filepath: str
    status: str
    original_filesize: int
    percent_saved: float

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def orig_file_size_h(self):
        return to_kilobytes(self.original_filesize)
        # return human(self.original_filesize)
