import os
from typing import List

from optimize_images_x.file_utils import search_images
from optimize_images_x.global_setup import COMPLETE
from optimize_images_x.task import Task


class AppStatus:
    """ A class which keeps references to GUI objects and application status.
    """

    def __init__(self):
        self.settings_window = None  # Saves a reference to the settings window object
        self.about_window = None  # Saves a reference to the about window object
        self.thanks_window = None  # Saves a reference to the thanks window object
        self.is_settings_window_open = False
        self.tasks: List[Task] = []
        self.filepaths = set()

    @property
    def processed_tasks_count(self):
        return sum(1 for x in self.tasks if x.status == COMPLETE)

    @property
    def tasks_count(self):
        return len(self.tasks)

    @property
    def tasks_total_filesize(self):
        return sum(t.original_filesize for t in self.tasks)

    @property
    def tasks_total_bytes_saved(self):
        return sum(t.bytes_saved for t in self.tasks if t.bytes_saved != 0)

    @property
    def tasks_total_percent_saved(self):
        if self.tasks_total_bytes_saved == 0:
            return 0
        else:
            return self.tasks_total_bytes_saved / self.tasks_total_filesize * 100

    def add_task(self, filepath):
        self._add_if_new(filepath, self.filepaths)

    def add_folder(self, path, recursive: bool):
        for filepath in search_images(path, recursive):
            self._add_if_new(filepath, self.filepaths)

    def _add_if_new(self, filepath, filepaths):
        if filepath not in filepaths:
            size = os.path.getsize(filepath)
            new_task = Task(filepath, 'Pending…', size, 0)
            self.tasks.append(new_task)
            self.filepaths.add(filepath)

    def clear_list(self):
        self.tasks = []
        self.filepaths = set()
