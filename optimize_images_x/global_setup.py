import os

# todo: account for windows paths...
DB_PATH = os.path.expanduser('~') + '/optimize_images_x_settings.sqlite'
DEFAULT_PATH = os.path.expanduser('~')

APP_PATH = 'xxx'
APP_NAME = 'Optimize Images X'
APP_LICENSE = 'copyright text'

CREDITS = """
    credits text
    sample text 
    more sample text
    """

SUPPORTED_TYPES = [
    ('All supported images', '.jpg .jpeg .png'),
    ('JPEG Images', '.jpeg'),
    ('JPEG Images', '.jpg'),
    ('PNG Images', '.png'),
]

SUPPORTED_FORMATS = ('jpg', 'jpeg', 'png')

PENDING = 0
IN_PROGRESS = 1
COMPLETE = 2

MAIN_MIN_WIDTH = 400
MAIN_MIN_HEIGHT = 250
MAIN_MAX_WIDTH = 2000
MAIN_MAX_HEIGHT = 2000
