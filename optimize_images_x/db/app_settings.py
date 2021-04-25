#!/usr/bin/env python3.6
# encoding: utf-8

from optimize_images_x.db.base import query_one, execute_with_params, reset_app_settings


class AppSettings:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.show_welcome_msg = True
        self.show_watch_msg = True
        self.main_window_x = 1
        self.main_window_y = 1
        self.main_window_w = 700
        self.main_window_h = 600
        self.app_style = 'clam'
        self.last_opened_dir = '~/'
        self.last_watched_dir = '~/'
        self.load()

    def load(self):
        sql = "SELECT * FROM app_settings"
        settings = query_one(self.db_path, sql)
        self.show_welcome_msg = settings['show_welcome_msg']
        self.show_watch_msg = settings['show_watch_msg']
        self.main_window_x = settings['main_window_x']
        self.main_window_y = settings['main_window_y']
        self.main_window_w = settings['main_window_w']
        self.main_window_h = settings['main_window_h']
        self.app_style = settings['app_style']
        self.last_opened_dir = settings['last_opened_dir']
        self.last_watched_dir = settings['last_watched_dir']

    def save(self):
        sql = """
            UPDATE app_settings 
            SET show_welcome_msg=?,
                show_watch_msg=?,
                main_window_x=?,
                main_window_y=?,
                main_window_w=?,
                main_window_h=?,
                app_style=?,
                last_opened_dir=?,
                last_watched_dir=?
            WHERE id=1
            """

        values = (self.show_welcome_msg,
                  self.show_watch_msg,
                  self.main_window_x,
                  self.main_window_y,
                  self.main_window_w,
                  self.main_window_h,
                  self.app_style,
                  self.last_opened_dir,
                  self.last_watched_dir)

        execute_with_params(self.db_path, sql, values)

    def reset(self):
        reset_app_settings(self.db_path)

    def __str__(self) -> str:
        return f"AppSettings: X: {self.main_window_x}, Y: {self.main_window_y}, " \
               f"W: {self.main_window_w}, H: {self.main_window_h}, " \
               f"Style: {self.app_style}"
