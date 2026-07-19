import os
import platform
import sys

import optimize_images_x.i18n as i18n

# Format support is reported by the engine, reflecting the codecs actually
# present in the Pillow build in use. We prefer the public api namespace, but
# fall back to the formats module (some engine builds expose the helpers only
# there) and, as a last resort, to a minimal set derived from Pillow directly,
# so the application never fails to start because of the engine packaging.
try:
    from optimize_images.api import (available_input_formats,
                                     available_output_formats)
except ImportError:
    try:
        from optimize_images.formats import (available_input_formats,
                                             available_output_formats)
    except ImportError:
        available_input_formats = available_output_formats = None

if available_input_formats is not None:
    INPUT_FORMATS = available_input_formats()
    OUTPUT_FORMATS = available_output_formats()
else:
    from PIL import features
    _webp = ['webp'] if features.check('webp') else []
    INPUT_FORMATS = ['jpg', 'jpeg', 'mpo', 'png'] + _webp
    OUTPUT_FORMATS = ['jpeg', 'png'] + _webp

WEBP_SUPPORTED = 'webp' in OUTPUT_FORMATS  # kept for backwards reference

# todo: account for windows paths...
DB_PATH = os.path.expanduser('~') + '/optimize_images_x_settings.sqlite'
DEFAULT_PATH = os.path.expanduser('~')

APP_PATH = 'xxx'


def APP_NAME():
    return i18n._("Optimize Images X")


def APP_LICENSE():
    return i18n._("MIT License")


def CREDITS():
    # Literal i18n._(...) calls, not a loop over a module-level list: Babel's
    # extractor only picks up calls with a string-literal argument (see the
    # same fix in gui/base_app.py's configure_tree() for the grid headers).
    return [
        i18n._(
            "Optimize Images X was initially created by Victor Domingos and both "
            "inspired and made possible by the work of many other developers, "
            "including the makers of existing image processing utilities, Pillow, "
            "as well as the direct contibutors to this project and to it's parent "
            "application, Optimize Images (the CLI version)."),
        i18n._("\nIcon theme from https://feathericons.com, copyrighted under "
              "the MIT licence."),
    ]


_ALL_EXT = ' '.join('.' + ext for ext in INPUT_FORMATS)
SUPPORTED_TYPES = [('All supported images', _ALL_EXT)]
SUPPORTED_TYPES += [(ext.upper() + ' Images', '.' + ext) for ext in INPUT_FORMATS]

SUPPORTED_FORMATS = tuple(INPUT_FORMATS)

PENDING = 0
IN_PROGRESS = 1
OPTIMIZED = 2
SKIPPED = 3
ERROR = 4

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