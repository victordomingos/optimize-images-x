import os
import platform
import sys

# todo: account for windows paths...
DB_PATH = os.path.expanduser('~') + '/optimize_images_x_settings.sqlite'
DEFAULT_PATH = os.path.expanduser('~')

APP_PATH = 'xxx'
APP_NAME = 'Optimize Images X'
APP_LICENSE = 'MIT License'

CREDITS = [
    "Optimize Images X was initially created by Victor Domingos and both "
    "inspired and made possible by the work of many other developers, "
    "including the makers of existing image processing utilities, Pillow, "
    "as well as the direct contibutors to this project and to it's parent "
    "application, Optimize Images (the CLI version).",
    "\nIcon theme from https://feathericons.com, copyrighted under the MIT licence."
]

SUPPORTED_TYPES = [
    ('All supported images', '.jpg .jpeg .png'),
    ('JPEG Images', '.jpeg'),
    ('JPEG Images', '.jpg'),
    ('PNG Images', '.png'),
]

SUPPORTED_FORMATS = ('jpg', 'jpeg', 'png')

PENDING = 0
IN_PROGRESS = 1
OPTIMIZED = 2
SKIPPED = 3

MAIN_MIN_WIDTH = 600
MAIN_MIN_HEIGHT = 250
MAIN_MAX_WIDTH = 2000
MAIN_MAX_HEIGHT = 4000


def text_color():
    """Text color that matches dark or bright mode on macOS."""
    if platform.system() == 'Darwin':
        return ''  # Aqua theme fills this in automatically
    return 'grey22'  # default color for other platforms or themes


def resource_path(relative):
    """Absolute path to a bundled resource, in frozen, pip or source contexts."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.join(sys._MEIPASS, 'optimize_images_x')
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def ui_font():
    """Native UI font family per platform (SF system font on macOS)."""
    if platform.system() == 'Darwin':
        return '-apple-system'
    return 'Helvetica'