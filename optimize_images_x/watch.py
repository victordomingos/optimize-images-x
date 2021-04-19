import os
import time
from typing import List

from watchdog.events import FileSystemEventHandler


def is_image(filepath):
    if not os.path.isfile(filepath):
        return False
    else:
        extension = os.path.splitext(filepath)[1][1:]
        return extension.lower() in ['jpg', 'jpeg', 'png']


class OptimizeImageEventHandler(FileSystemEventHandler):
    def __init__(self, parent):
        super().__init__()
        self.paths_to_ignore: List[str] = []
        self.new_files = 0
        self.optimized_files = 0
        self.total_bytes_saved = 0
        self.total_src_size = 0
        self.parent = parent

    def on_moved(self, event):
        self.parent.notify(event)

    def on_created(self, event):
        self.parent.notify(event)
        return

    @staticmethod
    def wait_for_write_finish(filename: str) -> None:
        """ Wait until file has been completely written (when file size stabilizes)
        """
        size = -1
        while size != os.stat(filename).st_size:
            size = os.stat(filename).st_size
            time.sleep(0.01)
