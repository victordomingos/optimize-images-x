#!/usr/bin/env python3
# encoding: utf-8
"""
A desktop app written in Python, that unlocks the power of Optimize Images in a
graphical user interface, to help you reduce the file size of images.

© 2021 Victor Domingos, MIT License
"""
import platform
import tkinter as tk
from tkinter import ttk

from gui.app_status import AppStatus
from gui.main_window import App
from optimize_images_x.db.app_settings import AppSettings
from optimize_images_x.db.base import initialize
from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import APP_NAME, DB_PATH

if __name__ == "__main__":
    initialize(DB_PATH, platform.system())

    app_status = AppStatus()
    app_settings = AppSettings(DB_PATH)
    task_settings = TaskSettings(DB_PATH)

    root = tk.Tk()
    app_status.main_window = App(root, app_status, app_settings, task_settings)

    estilo_global = ttk.Style(root)
    estilo_global.theme_use(app_settings.app_style)
    root.configure(background='grey95')
    root.title(APP_NAME)

    x = app_settings.main_window_x
    y = app_settings.main_window_y
    width = app_settings.main_window_w
    height = app_settings.main_window_h

    root.geometry(f"{width}x{height}+{x}+{y}")
    root.bind_all("<Mod2-q>", root.quit)

    root.mainloop()
