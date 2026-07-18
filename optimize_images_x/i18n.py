# encoding: utf-8
"""Internationalization support for Optimize Images X."""

import gettext
import os
import sys

APP_NAME = "Optimize Images X"
CREDITS = f"{APP_NAME} - Image optimization made easy.\n\n" \
          "© 2026 Victor Domingos, MIT License."

# Get the package directory. Under PyInstaller, __file__-based paths resolve
# inside the PYZ archive rather than the bundled data directory, so fall back
# to sys._MEIPASS (same approach as global_setup.resource_path()).
if hasattr(sys, '_MEIPASS'):
    PACKAGE_DIR = os.path.join(sys._MEIPASS, 'optimize_images_x')
else:
    PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALE_DIR = os.path.join(PACKAGE_DIR, 'locale')

# Initialize gettext
gettext.bindtextdomain('optimize_images_x', LOCALE_DIR)
gettext.textdomain('optimize_images_x')

# Create a translation function
_trans = gettext.translation(
    'optimize_images_x',
    localedir=LOCALE_DIR,
    fallback=True
)

_ = _trans.gettext
ngettext_func = _trans.ngettext


def change_language(lang_code):
    """Change the application language at runtime.

    Args:
        lang_code: Language code (e.g., 'pt', 'en') or None for default
    """
    global _trans, _, ngettext_func

    if lang_code and lang_code.lower() != 'en':
        try:
            _trans = gettext.translation(
                'optimize_images_x',
                localedir=LOCALE_DIR,
                languages=[lang_code],
                fallback=True
            )
            _ = _trans.gettext
            ngettext_func = _trans.ngettext
        except FileNotFoundError:
            # If language not available, fall back to English (source strings)
            _ = lambda msg: msg
            ngettext_func = lambda s, p, n: s if n == 1 else p
    else:
        # English is the source language — no translation needed
        _ = lambda msg: msg
        ngettext_func = lambda s, p, n: s if n == 1 else p


def get_translated_app_name():
    """Get the app name in the current locale."""
    return _(APP_NAME)


def get_translated_credits():
    """Get the credits text in the current locale."""
    return _(CREDITS)


def get_available_languages():
    """Get list of available language codes.
    
    Returns:
        List of language codes (e.g., ['pt', 'en'])
    """
    import os

    languages = []

    if os.path.exists(LOCALE_DIR):
        for item in os.listdir(LOCALE_DIR):
            if os.path.isdir(os.path.join(LOCALE_DIR, item)):
                # Check if it's a language directory (has LC_MESSAGES subdirectory)
                lc_dir = os.path.join(LOCALE_DIR, item, 'LC_MESSAGES')
                if os.path.exists(lc_dir):
                    languages.append(item)

    return sorted(languages) if languages else []
