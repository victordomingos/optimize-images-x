import os
from typing import List, Tuple

from optimize_images_x.global_setup import OPTIMIZED, PENDING, SKIPPED
from optimize_images_x.search_images import search_images
from optimize_images_x.task import Task


class AppStatus:
    """ A class which keeps references to GUI objects and application status.
    """

    def __init__(self):
        self.settings_window = None  # Saves a reference to the settings window object
        self.about_window = None  # Saves a reference to the about window object
        self.thanks_window = None  # Saves a reference to the thanks window object
        self.main_window = None
        self.is_settings_window_open = False
        self.tasks: List[Task] = []
        self.filepaths = set()

    @property
    def processed_tasks_count(self):
        return sum(1 for x in self.tasks if x.status == OPTIMIZED)

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

    def add_task(self, filepath, status=PENDING, original_size=0, final_size=0) -> Tuple[int, int]:
        return self._add_if_new(filepath, self.filepaths, status, original_size, final_size)

    def add_folder(self, path, recursive: bool) -> Tuple[int, int]:
        added_imgs = 0
        total_added_bytes = 0
        for filepath in search_images(path, recursive):
            added_img, added_bytes = self._add_if_new(filepath, self.filepaths)
            added_imgs += added_img
            total_added_bytes += added_bytes

        return added_imgs, total_added_bytes

    def _add_if_new(self, filepath, filepaths, status=PENDING, original_size=0, final_size=0) -> Tuple[int, int]:
        if filepath in filepaths:
            return 0, 0

        if original_size == 0:
            size = os.path.getsize(filepath)
        else:
            size = original_size

        new_task = Task(filepath, status, size, final_size)
        self.tasks.append(new_task)
        self.filepaths.add(filepath)
        return 1, size

    def clear_list(self):
        self.tasks = []
        self.filepaths = set()

    def update_task(self, result_task):
        index = next((i for i, task in enumerate(self.tasks)
                      if task.filepath == result_task.img), None)

        task = self.tasks[index]
        if task.filepath == result_task.img:
            if result_task.was_optimized:
                task.status = OPTIMIZED
                task.final_filesize = result_task.final_size
            else:
                task.status = SKIPPED
            return
