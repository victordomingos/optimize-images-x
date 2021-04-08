import os
from dataclasses import dataclass
from typing import List

from optimize_images_x.global_setup import COMPLETE, PENDING


class AppStatus:
    """ A class which keeps references to GUI objects and application status.
    """

    def __init__(self):
        self.settings_window = None  # Saves a reference to the settings window object
        self.about_window = None  # Saves a reference to the about window object
        self.thanks_window = None  # Saves a reference to the thanks window object
        self.tasks: List[Task] = []

    @property
    def processed_tasks_count(self):
        return sum(1 for x in self.tasks if x.status == COMPLETE)

    @property
    def tasks_count(self):
        return len(self.tasks)

    def add_task(self, filepath):
        filepaths = (t.filepath for t in self.tasks)
        if filepath not in filepaths:
            new_task = Task(filepath, PENDING, os.path.getsize(filepath), 0)
            self.tasks.append(new_task)


@dataclass
class Task:
    filepath: str
    status: int
    original_filesize: int
    percent_saved: float

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def orig_file_size_h(self):
        return self.human(self.original_filesize)

    @staticmethod
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
