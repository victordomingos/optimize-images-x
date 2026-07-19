# encoding: utf-8
"""Image information for display, delegating to the optimize-images engine.

The engine is the source of truth about image files: ``inspect_image()``
provides the intrinsic properties and raw EXIF, and ``format_exif()`` renders
EXIF values using standardized semantics. This module only adapts that data
for presentation (labels and section titles), so it stays a thin layer with
no image-reading logic of its own.
"""
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from optimize_images.api import inspect_image, format_exif

import optimize_images_x.i18n as i18n


def _exif_section_titles():
    # Evaluated per call, not at import time: a module-level dict would
    # freeze these under whatever language was active on first import (see
    # localization-dev.md's note on module-level _() calls).
    return {'image': i18n._('Image'), 'camera': i18n._('Camera'),
            'gps': i18n._('GPS')}


@dataclass(frozen=True)
class ImageInfo:
    filepath: str
    image_format: str
    width: int
    height: int
    filesize: int
    properties: Dict[str, str]            # label -> display value
    exif: Dict[str, Dict[str, str]]       # section title -> {tag: value}

    @property
    def filename(self) -> str:
        return os.path.basename(self.filepath)

    @property
    def folder(self) -> str:
        return os.path.dirname(self.filepath)


def read_image_info(filepath: str) -> ImageInfo:
    """Build an ImageInfo for display. Propagates OSError if unreadable."""
    meta = inspect_image(filepath)

    yes, no = i18n._('yes'), i18n._('no')
    props: Dict[str, str] = {
        i18n._('Format'): meta.image_format or i18n._('Unknown'),
        i18n._('Mode'): meta.mode,
        i18n._('Dimensions'): f'{meta.width} x {meta.height} px',
        i18n._('Alpha'): yes if meta.has_alpha else no,
    }
    if meta.palette_colors is not None:
        props[i18n._('Palette colors')] = str(meta.palette_colors)
    if meta.is_progressive is not None:
        props[i18n._('Progressive')] = yes if meta.is_progressive else no
    if meta.is_interlaced is not None:
        props[i18n._('Interlaced')] = yes if meta.is_interlaced else no
    props[i18n._('Frames')] = (
        f'{meta.n_frames} ({i18n._("animated")})' if meta.is_animated
        else str(meta.n_frames))
    if meta.dpi:
        props[i18n._('DPI')] = f'{meta.dpi[0]:g} x {meta.dpi[1]:g}'
    icc_description = getattr(meta, 'icc_profile_description', None)
    props[i18n._('ICC profile')] = icc_description or \
        (yes if meta.has_icc_profile else no)

    stats = os.stat(filepath)
    created = getattr(stats, 'st_birthtime', None)  # real creation on macOS
    if created is None:
        created = stats.st_ctime
    props[i18n._('Created')] = _format_date(created)
    props[i18n._('Modified')] = _format_date(stats.st_mtime)

    section_titles = _exif_section_titles()
    exif = {section_titles.get(section, section.title()): dict(tags)
            for section, tags in format_exif(meta.exif).items()}

    return ImageInfo(filepath=filepath,
                     image_format=meta.image_format,
                     width=meta.width,
                     height=meta.height,
                     filesize=stats.st_size,
                     properties=props,
                     exif=exif)


def _format_date(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')