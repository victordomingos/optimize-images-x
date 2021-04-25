#!/usr/bin/env python3.6
# encoding: utf-8

from optimize_images_x.db.base import query_one, execute_with_params, reset_task_settings


class TaskSettings:
    def __init__(self, db_path: str):
        self.db_path = db_path

        self.keep_original_size = True
        self.max_width = 1600
        self.max_height = 1000
        self.recurse_subfolders = True
        self.fast_mode = False
        self.convert_grayscale = False
        self.no_comparison = False
        self.n_jobs = 0
        self.auto_jobs = True

        # JPEG Settings
        self.jpg_dynamic_quality = True
        self.jpg_quality = 85
        self.keep_exif = False

        # PNG settings
        self.convert_big_to_jpg = False
        self.convert_all_to_jpg = False
        self.force_delete = False
        self.reduce_colors = False
        self.max_colors = 255
        self.remove_transparency = False
        self.bg_color_red = 255
        self.bg_color_green = 255
        self.bg_color_blue = 255
        self.bg_color_hex = '#FFFFFF'

        self.load()

    def load(self):
        sql = "SELECT * FROM Task_Settings"
        settings = query_one(self.db_path, sql)

        self.keep_original_size = settings['keep_original_size']
        self.max_width = settings['max_width']
        self.max_height = settings['max_height']
        self.recurse_subfolders = settings['recurse_subfolders']
        self.fast_mode = settings['fast_mode']
        self.convert_grayscale = settings['convert_grayscale']
        self.no_comparison = settings['no_comparison']
        self.n_jobs = settings['n_jobs']
        self.auto_jobs = settings['auto_jobs']

        # JPEG Settings
        self.jpg_dynamic_quality = settings['jpg_dynamic_quality']
        self.jpg_quality = settings['jpg_quality']
        self.keep_exif = settings['keep_exif']

        # PNG settings
        self.convert_big_to_jpg = settings['convert_big_to_jpg']
        self.convert_all_to_jpg = settings['convert_all_to_jpg']
        self.force_delete = settings['force_delete']
        self.reduce_colors = settings['reduce_colors']
        self.max_colors = settings['max_colors']
        self.remove_transparency = settings['remove_transparency']
        self.bg_color_red = settings['bg_color_red']
        self.bg_color_green = settings['bg_color_green']
        self.bg_color_blue = settings['bg_color_blue']
        self.bg_color_hex = settings['bg_color_hex']

    def save(self):
        sql = """
            UPDATE task_settings 
            SET keep_original_size=?,
                max_width=?,
                max_height=?,
                recurse_subfolders=?,
                fast_mode=?,
                convert_grayscale=?,
                no_comparison=?,
                n_jobs=?,
                auto_jobs=?,
                
                jpg_dynamic_quality=?,
                jpg_quality=?,
                keep_exif=?,
                
                convert_big_to_jpg=?,
                convert_all_to_jpg=?,
                force_delete=?,
                reduce_colors=?,
                max_colors=?,
                remove_transparency=?,
                bg_color_red=?,
                bg_color_green=?,
                bg_color_blue=?,
                bg_color_hex=?
            WHERE id=1
            """

        values = (self.keep_original_size,
                  self.max_width,
                  self.max_height,
                  self.recurse_subfolders,
                  self.fast_mode,
                  self.convert_grayscale,
                  self.no_comparison,
                  self.n_jobs,
                  self.auto_jobs,

                  self.jpg_dynamic_quality,
                  self.jpg_quality,
                  self.keep_exif,

                  self.convert_big_to_jpg,
                  self.convert_all_to_jpg,
                  self.force_delete,
                  self.reduce_colors,
                  self.max_colors,
                  self.remove_transparency,
                  self.bg_color_red,
                  self.bg_color_green,
                  self.bg_color_blue,
                  self.bg_color_hex,
                  )

        execute_with_params(self.db_path, sql, values)

    def reset(self):
        reset_task_settings(self.db_path)
