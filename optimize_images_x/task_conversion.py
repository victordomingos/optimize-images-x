from typing import Union

from optimize_images.data_structures import Task as OITask, TaskResult

from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import IN_PROGRESS
from optimize_images_x.global_setup import OPTIMIZED, SKIPPED
from optimize_images_x.task import Task


def convert_task(task: Union[Task, str], task_settings: TaskSettings) -> OITask:
    path: str
    if isinstance(task, Task):
        task.status = IN_PROGRESS
        path = task.filepath
    elif isinstance(task, str):
        path = task
    else:
        msg = f'Argument must be of either type Task or str, not {type(task)}.'
        raise TypeError(msg)

    if task_settings.keep_original_size:
        max_width = 0
        max_height = 0
    else:
        max_width = task_settings.max_width
        max_height = task_settings.max_height

    return OITask(path,
                  task_settings.jpg_quality,
                  task_settings.remove_transparency,
                  task_settings.reduce_colors,
                  task_settings.max_colors,
                  max_width,
                  max_height,
                  task_settings.keep_exif,
                  task_settings.convert_all_to_jpg,
                  task_settings.convert_big_to_jpg,
                  task_settings.force_delete,
                  (task_settings.bg_color_red,
                   task_settings.bg_color_green,
                   task_settings.bg_color_blue),
                  task_settings.convert_grayscale,
                  task_settings.no_comparison,
                  task_settings.fast_mode)


def get_task_icon(task: Union[Task, TaskResult]) -> str:
    if isinstance(task, TaskResult):
        return '✅' if task.was_optimized else '❌'
    elif isinstance(task, Task):
        if task.status == OPTIMIZED:
            return '✅'
        elif task.status == SKIPPED:
            return '❌'

    return ''
