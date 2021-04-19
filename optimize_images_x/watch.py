import os
import time
from typing import List, Tuple

from optimize_images.data_structures import Task, TaskResult
from optimize_images.do_optimization import do_optimization
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import OPTIMIZED, SKIPPED


def is_image(filepath):
    if not os.path.isfile(filepath):
        return False
    else:
        extension = os.path.splitext(filepath)[1][1:]
        return extension.lower() in ['jpg', 'jpeg', 'png']


class OptimizeImageEventHandler(FileSystemEventHandler):
    def __init__(self, folder: str, task_settings: TaskSettings, parent):
        super().__init__()
        self.folder = folder
        self.task_settings = task_settings
        self.paths_to_ignore: List[str] = []
        self.new_files = 0
        self.optimized_files = 0
        self.total_bytes_saved = 0
        self.total_src_size = 0
        self.parent = parent

    def on_created(self, event):
        if (event.is_directory
                or not is_image(event.src_path)
                or '~temp~' in event.src_path
                or event.src_path in self.paths_to_ignore):
            return

        self.paths_to_ignore.append(event.src_path)
        self.wait_for_write_finish(event.src_path)
        self.new_files += 1

        if self.task_settings.keep_original_size:
            max_width = 0
            max_height = 0
        else:
            max_width = self.task_settings.max_width
            max_height = self.task_settings.max_height

        img_task = Task(event.src_path,
                        self.task_settings.jpg_quality,
                        self.task_settings.remove_transparency,
                        self.task_settings.reduce_colors,
                        self.task_settings.max_colors,
                        max_width,
                        max_height,
                        self.task_settings.keep_exif,
                        self.task_settings.convert_all_to_jpg,
                        self.task_settings.convert_big_to_jpg,
                        self.task_settings.force_delete,
                        (self.task_settings.bg_color_red,
                         self.task_settings.bg_color_green,
                         self.task_settings.bg_color_blue),
                        self.task_settings.convert_grayscale,
                        self.task_settings.no_comparison,
                        self.task_settings.fast_mode)

        result: TaskResult = do_optimization(img_task)
        self.total_src_size += result.orig_size

        if result.was_optimized:
            added_imgs, added_bytes = \
                self.parent.app_status.add_task(filepath=result.img,
                                                status=OPTIMIZED,
                                                original_size=result.orig_size,
                                                final_size=result.final_size)
            self.optimized_files += 1
            self.total_bytes_saved += result.orig_size - result.final_size
        else:
            added_imgs, added_bytes = \
                self.parent.app_status.add_task(filepath=result.img,
                                                status=SKIPPED,
                                                original_size=result.orig_size,
                                                final_size=result.final_size)

        self.parent.update_img_list()
        self.parent.app_stats.update_load_stats(added_imgs, added_bytes)

    @staticmethod
    def wait_for_write_finish(filename: str) -> None:
        """ Wait until file has been completely written (when file size stabilizes)
        """
        size = -1
        while size != os.stat(filename).st_size:
            size = os.stat(filename).st_size
            time.sleep(0.01)


def watch_for_new_files(path: str, task_settings: TaskSettings, parent) -> Tuple[Observer, OptimizeImageEventHandler]:
    folder = os.path.abspath(path)
    event_handler = OptimizeImageEventHandler(folder, task_settings, parent)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    return observer, event_handler


def stop_watching(observer):
    observer.stop()
    observer.join()
