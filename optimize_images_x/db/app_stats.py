#!/usr/bin/env python3.6
# encoding: utf-8

from optimize_images_x.db.base import query_one, execute_with_params


class AppStats:
    def __init__(self, db_path: str):
        self.db_path = db_path

        self.images_loaded = 0
        self.images_processed = 0
        self.processing_time: float = 0.0
        self.total_weight_loaded = 0
        self.total_weight_processed = 0
        self.total_weight_saved = 0
        self.session_count = 0
        self.sessions_with_processed = 0

        self.load()

    def load(self):
        sql = "SELECT * FROM App_Stats"
        settings = query_one(self.db_path, sql)

        self.images_loaded = settings['images_loaded']
        self.images_processed = settings['images_processed']
        self.processing_time = settings['processing_time']
        self.total_weight_loaded = settings['total_weight_loaded']
        self.total_weight_processed = settings['total_weight_processed']
        self.total_weight_saved = settings['total_weight_saved']
        self.session_count = settings['session_count']
        self.sessions_with_processed = settings['sessions_with_processed']

    def save(self):
        sql = """
            UPDATE App_Stats 
            SET images_loaded=?,
                images_processed=?,
                processing_time=?,
                total_weight_loaded=?,
                total_weight_processed=?,
                total_weight_saved=?,
                session_count=?,
                sessions_with_processed=?
            WHERE id=1
            """

        values = (self.images_loaded,
                  self.images_processed,
                  self.processing_time,
                  self.total_weight_loaded,
                  self.total_weight_processed,
                  self.total_weight_saved,
                  self.session_count,
                  self.sessions_with_processed)

        execute_with_params(self.db_path, sql, values)

    def update_load_stats(self, images_loaded: int, total_weight_loaded: int):
        self.images_loaded += images_loaded
        self.total_weight_loaded += total_weight_loaded
        self.save()

    def update_process_stats(self, images_processed: int, processing_time: float,
                             total_weight_processed: int, total_weight_saved: int):
        self.images_processed += images_processed
        self.processing_time += processing_time
        self.total_weight_processed += total_weight_processed
        self.total_weight_saved += total_weight_saved
        if images_processed > 0:
            self.sessions_with_processed += 1
        self.save()
