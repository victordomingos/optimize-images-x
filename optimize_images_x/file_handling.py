# encoding: utf-8
"""Small helpers for handing files to the operating system."""
import os
import platform
import subprocess


def open_in_default_viewer(filepath: str) -> None:
    """Open the actual file in the system's default application.

    Unlike PIL's ``Image.show()``, which saves a temporary PNG copy and opens
    that, this hands the real file to the OS, so the viewer shows the true
    image (same name, format and location).
    """
    system = platform.system()
    if system == 'Darwin':
        subprocess.run(['open', filepath])
    elif system == 'Windows':
        os.startfile(filepath)  # pylint: disable=no-member
    else:
        subprocess.run(['xdg-open', filepath])