#!/usr/bin/env python3
# encoding: utf-8
"""
A desktop app written in Python, that unlocks the power of Optimize Images in a
graphical user interface, to help you reduce the file size of images.

© 2026 Victor Domingos, MIT License
"""
import multiprocessing
import platform
import tkinter as tk
from tkinter import ttk

from optimize_images_x.db.app_settings import AppSettings
from optimize_images_x.db.app_stats import AppStats
from optimize_images_x.db.base import initialize
from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import DB_PATH
from optimize_images_x.i18n import change_language
from optimize_images_x.gui.app_status import AppStatus
from optimize_images_x.gui.main_window import App

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = None
    DND_AVAILABLE = False


def main():
    multiprocessing.freeze_support()
    initialize(DB_PATH)
    app_status = AppStatus()
    app_settings = AppSettings(DB_PATH)
    task_settings = TaskSettings(DB_PATH)
    app_stats = AppStats(DB_PATH)

    app_stats.session_count += 1
    app_stats.save()

    change_language(app_settings.language or 'en')

    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app_status.main_window = App(root, app_status, app_settings,
                                 task_settings, app_stats)

    global_style = ttk.Style(root)
    # global_style.theme_use('clam')
    # global_style.theme_use('classic')
    global_style.theme_use(app_settings.app_style)
    root.mainloop()


if __name__ == "__main__":
    main()