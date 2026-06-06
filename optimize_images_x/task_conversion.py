from typing import Union

from optimize_images.api import PublicTaskResult

from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import IN_PROGRESS
from optimize_images_x.global_setup import OPTIMIZED, SKIPPED
from optimize_images_x.task import Task


def build_options(task_settings: TaskSettings) -> dict:
    """Map app settings to the public API arguments."""
    if task_settings.keep_original_size:
        max_width = 0
        max_height = 0
    else:
        max_width = task_settings.max_width
        max_height = task_settings.max_height

    return dict(
        quality=task_settings.jpg_quality,
        remove_transparency=task_settings.remove_transparency,
        reduce_colors=task_settings.reduce_colors,
        max_colors=task_settings.max_colors,
        max_w=max_width,
        max_h=max_height,
        keep_exif=task_settings.keep_exif,
        convert_all=task_settings.convert_all_to_jpg,
        conv_big=task_settings.convert_big_to_jpg,
        force_del=task_settings.force_delete,
        bg_color=(task_settings.bg_color_red,
                  task_settings.bg_color_green,
                  task_settings.bg_color_blue),
        grayscale=task_settings.convert_grayscale,
        ignore_size_comparison=task_settings.no_comparison,
        fast_mode=task_settings.fast_mode,
        convert_to=task_settings.convert_to,
        webp_quality=task_settings.webp_quality,
        webp_lossless=bool(task_settings.webp_lossless),
        webp_method=task_settings.webp_method,
    )


def resolve_path(task: Union[Task, str]) -> str:
    """Extract filepath e mark the task as in progress."""
    if isinstance(task, Task):
        task.status = IN_PROGRESS
        return task.filepath
    elif isinstance(task, str):
        return task
    msg = f'Argument must be of either type Task or str, not {type(task)}.'
    raise TypeError(msg)


def get_task_icon(task: Union[Task, PublicTaskResult]) -> str:
    if isinstance(task, PublicTaskResult):
        return '✅' if task.was_optimized else '❌'
    elif isinstance(task, Task):
        if task.status == OPTIMIZED:
            return '✅'
        elif task.status == SKIPPED:
            return '❌'
    return ''