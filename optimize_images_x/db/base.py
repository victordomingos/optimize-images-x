# encoding: utf-8
import platform
import sqlite3
from contextlib import closing
from os import cpu_count
from typing import Any


def execute(db_path: str, sql: str) -> None:
    """ Execute a SQL script, with no return value.

    @param db_path: path to the database file
    @param sql: the SQL instructions
    """
    with closing(sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)) as conn:
        conn.executescript(sql)


def execute_with_params(db_path: str, sql: str, values=None) -> None:
    """ Execute a SQL script, with no return value.

    @param values: sql parameters to the execute command (e.g. values)
    @param db_path: path to the database file
    @param sql: the SQL instructions
    """
    if values is None:
        values = []

    with closing(sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)) as conn:
        conn.execute(sql, values)
        conn.commit()


def query_one(db_path: str, sql: str) -> Any:
    """ Execute a SQL query and return the first row.

        @param db_path: path to the database file
        @param sql: the SQL query
        """
    with closing(sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            row = cursor.execute(sql).fetchone()

    return row


def initialize(db_path: str) -> None:
    """ Create the database file, generate tables and populate default values.

    If the database file does not exist, it will be created. Then, each of the
    tables is created, and in case no record exists yet, default values are
    filled up.

    @param db_path: path to the database file
    """
    current_platform = platform.system()

    if current_platform == 'Darwin':
        default_app_style = 'aqua'
    elif current_platform == 'Windows':
        default_app_style = 'vista'
    else:
        default_app_style = 'clam'

    n_jobs = cpu_count()

    sql_script = f"""
        CREATE TABLE IF NOT EXISTS app_settings 
        (
            id                 INTEGER UNIQUE PRIMARY KEY   DEFAULT 1,
            show_welcome_msg   BOOLEAN   DEFAULT TRUE, 
            show_watch_msg     BOOLEAN   DEFAULT TRUE, 
            main_window_x      INTEGER   DEFAULT 0,
            main_window_y      INTEGER   DEFAULT 0,
            main_window_w      INTEGER   DEFAULT 600,
            main_window_h      INTEGER   DEFAULT 340,
            app_style          TEXT,
            last_opened_dir    TEXT,
            last_watched_dir   TEXT
        );

        INSERT OR IGNORE INTO app_settings 
        (
             id, 
             show_welcome_msg, show_watch_msg, 
             main_window_x, main_window_y, main_window_w, main_window_h, 
             app_style, 
             last_opened_dir, last_watched_dir
        )
        VALUES 
        (
            1, 
            1, 1,
            0, 0, 600, 340,
            '{default_app_style}', 
            '', ''
        );

            
        CREATE TABLE IF NOT EXISTS task_settings 
        (
            id                   INTEGER UNIQUE PRIMARY KEY   DEFAULT 1,
            keep_original_size   BOOLEAN   DEFAULT TRUE,
            max_width            INTEGER   DEFAULT 1600,
            max_height           INTEGER   DEFAULT 1000,
            recurse_subfolders   BOOLEAN   DEFAULT TRUE,
            fast_mode            BOOLEAN   DEFAULT FALSE,
            convert_grayscale    BOOLEAN   DEFAULT FALSE,
            no_comparison        BOOLEAN   DEFAULT FALSE,
            n_jobs               INTEGER   DEFAULT 0,    
            auto_jobs            BOOLEAN   DEFAULT TRUE,    
            
            -- JPEG Settings
            jpg_dynamic_quality  BOOLEAN   DEFAULT TRUE,
            jpg_quality          INTEGER   DEFAULT 85,
            keep_exif            BOOLEAN   DEFAULT FALSE,
            
            -- PNG settings
            convert_big_to_jpg   BOOLEAN   DEFAULT FALSE,
            convert_all_to_jpg   BOOLEAN   DEFAULT FALSE,
            force_delete         BOOLEAN   DEFAULT FALSE,
            reduce_colors        BOOLEAN   DEFAULT FALSE,  -- (=auto)
            max_colors           INTEGER   DEFAULT 255,
            remove_transparency  BOOLEAN   DEFAULT FALSE,
            bg_color_red         INTEGER   DEFAULT 255,
            bg_color_green       INTEGER   DEFAULT 255,
            bg_color_blue        INTEGER   DEFAULT 255,
            bg_color_hex         TEXT      DEFAULT '#FFFFFF'
            );
            
        INSERT OR IGNORE INTO task_settings 
        (
            id,
            keep_original_size,
            max_width,
            max_height,
            recurse_subfolders,
            fast_mode,
            convert_grayscale,
            no_comparison,
            n_jobs,
            auto_jobs,
            
            -- JPEG Settings
            jpg_dynamic_quality,
            jpg_quality,
            keep_exif,
            
            -- PNG settings
            convert_big_to_jpg,
            convert_all_to_jpg,
            force_delete,
            reduce_colors,
            max_colors,
            remove_transparency,
            bg_color_red, bg_color_green, bg_color_blue,
            bg_color_hex
        )
        VALUES (
            1,
            1,
            1600,
            1000,
            1,
            0,
            0,
            0,
            {n_jobs},
            1,
            
            -- JPEG Settings
            1,
            85,
            0,
            
            -- PNG settings
            0,
            0,
            0,
            0,
            255,
            0,
            255, 255, 255,
            '#FFFFFF'
        );
            
        CREATE TABLE IF NOT EXISTS app_stats (
            id                       INTEGER UNIQUE PRIMARY KEY   DEFAULT 1,
            images_loaded            INTEGER  DEFAULT 0,
            images_processed         INTEGER  DEFAULT 0, -- optimized & saved imgs
            processing_time          REAL     DEFAULT 0, -- in seconds
            total_weight_loaded      INTEGER  DEFAULT 0, -- in bytes
            total_weight_processed   INTEGER  DEFAULT 0, -- in bytes
            total_weight_saved       INTEGER  DEFAULT 0, -- in bytes
            session_count            INTEGER  DEFAULT 0, -- all app sessions
            sessions_with_processed  INTEGER  DEFAULT 0 -- sessions width/processed imgs
            );
            
        INSERT OR IGNORE INTO app_stats
        (
            id,
            images_loaded,
            images_processed,
            processing_time,
            total_weight_loaded,
            total_weight_processed,
            total_weight_saved,
            session_count,
            sessions_with_processed
        )
        values
        (
            1,
            0, 0, 0,0,0,0,0,0
        );
        """

    execute(db_path, sql_script)


def reset_task_settings(db_path: str) -> None:
    """ Reset all settings to default values.

    @param db_path: path to the database file
    """
    n_jobs = cpu_count()

    sql_script = f"""
        INSERT OR REPLACE INTO task_settings 
        (
            id,
            keep_original_size,
            max_width,
            max_height,
            recurse_subfolders,
            fast_mode,
            convert_grayscale,
            no_comparison,
            n_jobs,
            auto_jobs,

            -- JPEG Settings
            jpg_dynamic_quality,
            jpg_quality,
            keep_exif,

            -- PNG settings
            convert_big_to_jpg,
            convert_all_to_jpg,
            force_delete,
            reduce_colors,
            max_colors,
            remove_transparency,
            bg_color_red, bg_color_green, bg_color_blue
        )
        VALUES (
            1,
            1,
            1600,
            1000,
            1,
            0,
            0,
            0,
            {n_jobs},
            1,
            
            -- JPEG Settings
            1,
            85,
            0,

            -- PNG settings
            0,
            0,
            0,
            0,
            255,
            0,
            255, 255, 255
        );
        """

    execute(db_path, sql_script)


def reset_app_settings(db_path: str) -> None:
    """ Reset all settings to default values.

    @param db_path: path to the database file
    """
    current_platform = platform.system()

    if current_platform == 'Darwin':
        default_app_style = 'aqua'
    elif current_platform == 'Windows':
        default_app_style = 'vista'
    else:
        default_app_style = 'clam'

    sql_script = f"""
        INSERT OR REPLACE INTO app_settings 
        (
             id, 
             show_welcome_msg, show_watch_msg, 
             main_window_x, main_window_y, main_window_w, main_window_h, 
             app_style, 
             last_opened_dir, last_watched_dir
        )
        VALUES 
        (
            1, 
            1, 1, 
            1, 1, 700, 600, 
            '{default_app_style}', 
            '',''
        );
        """
    execute(db_path, sql_script)


if __name__ == '__main__':
    from optimize_images_x.global_setup import DB_PATH

    # initialize(DB_PATH, 'macOS')
    # reset_settings(DB_PATH)

    print(query_one(DB_PATH, "SELECT * FROM app_settings;"))
    print(query_one(DB_PATH, "SELECT * FROM task_settings;"))
    print(query_one(DB_PATH, "SELECT * FROM app_stats;"))
