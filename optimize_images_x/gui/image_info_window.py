# encoding: utf-8
"""A non-modal window showing detailed information about one image.

Layout: an always-visible header (thumbnail, filename, folder, basic facts
and, for already processed images, a space-saving bar) above a ttk.Notebook
with two tabs: "Details" (optimization and image properties) and "EXIF"
(a tree grouped into the standardized Image / Camera / GPS sections).

One window per image; asking for the same image again just raises the
existing window. Data comes from the optimize-images engine through
optimize_images_x.image_info.
"""
import platform
import tkinter as tk
import tkinter.font
from tkinter import ttk
from typing import Dict, Optional

from PIL import Image, ImageTk

from optimize_images_x.calcs import human
from optimize_images_x.file_handling import open_in_default_viewer
from optimize_images_x.global_setup import OPTIMIZED
from optimize_images_x.gui.extra_tk_utilities.tooltips import add_tooltip
from optimize_images_x.image_info import read_image_info
from optimize_images_x.task import Task

THUMBNAIL_MAX_SIZE = (150, 112)
SAVINGS_BAR_SIZE = (220, 8)
FILENAME_MAX_CHARS = 42
FOLDER_MAX_CHARS = 52

_bold_font = None


def _get_bold_font():
    """A single shared bold variant of the default font (created once;
    Tk named fonts live for the whole process, so per-window copies would
    accumulate)."""
    global _bold_font
    if _bold_font is None:
        _bold_font = tkinter.font.nametofont('TkDefaultFont').copy()
        _bold_font.configure(weight='bold')
    return _bold_font


def middle_ellipsis(text: str, max_chars: int) -> str:
    """Shorten long text by cutting it in the middle (like macOS Finder),
    so windows keep a sane width."""
    if len(text) <= max_chars:
        return text
    keep = max_chars - 1
    head = (keep + 1) // 2
    tail = keep - head
    return f'{text[:head]}…{text[-tail:]}'


class ImageInfoWindow:
    """ Shows intrinsic properties, optimization results and EXIF metadata
    for a single image. Non-modal; one instance per image path.
    """
    _open_windows: Dict[str, 'ImageInfoWindow'] = {}

    @classmethod
    def show(cls, master, filepath: str,
             task: Optional[Task] = None) -> 'ImageInfoWindow':
        """ Open (or raise, if already open) the info window for an image.

        May propagate OSError if the image cannot be read; callers should
        handle it and inform the user.
        """
        existing = cls._open_windows.get(filepath)
        if existing is not None and existing.window.winfo_exists():
            existing.window.lift()
            existing.window.focus_force()
            return existing
        new_window = cls(master, filepath, task)
        cls._open_windows[filepath] = new_window
        return new_window

    def __init__(self, master, filepath: str, task: Optional[Task]):
        self.filepath = filepath
        self.task = task
        self.info = read_image_info(filepath)

        self.window = tk.Toplevel(master)
        self.window.title(f'Image info — {self.info.filename}')
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        if platform.system() == 'Darwin':
            self.window.bind('<Command-w>', self.close)
        else:
            self.window.bind('<Control-w>', self.close)

        self.bold_font = _get_bold_font()
        self.muted_color = '#777777'

        self._mount_header()
        self._build_body()
        self.window.update_idletasks()
        self.window.minsize(self.window.winfo_reqwidth(),
                            self.window.winfo_reqheight())

    def close(self, *event):
        ImageInfoWindow._open_windows.pop(self.filepath, None)
        self.window.destroy()

    # -- Header ---------------------------------------------------------
    def _mount_header(self):
        header = ttk.Frame(self.window, padding=(12, 12, 12, 6))
        header.pack(fill='x')

        thumb = self._make_thumbnail(header)
        thumb.grid(row=0, column=0, rowspan=4, sticky='nw', padx=(0, 14))
        thumb.bind('<Double-1>',
                   lambda event: open_in_default_viewer(self.filepath))
        add_tooltip(thumb, 'Double-click to open the image')

        name_label = ttk.Label(
            header,
            text=middle_ellipsis(self.info.filename, FILENAME_MAX_CHARS),
            font=self.bold_font)
        name_label.grid(row=0, column=1, sticky='w')

        folder_label = ttk.Label(
            header,
            text=middle_ellipsis(self.info.folder, FOLDER_MAX_CHARS),
            foreground=self.muted_color)
        folder_label.grid(row=1, column=1, sticky='w')
        add_tooltip(folder_label, self.filepath)
        if len(self.info.filename) > FILENAME_MAX_CHARS:
            add_tooltip(name_label, self.info.filename)

        facts = (f'{self.info.image_format or "Unknown"} · '
                 f'{self.info.width} x {self.info.height} px · '
                 f'{human(self.info.filesize)}')
        ttk.Label(header, text=facts).grid(row=2, column=1, sticky='w',
                                           pady=(4, 0))

        if self._is_optimized():
            self._mount_savings_bar(header).grid(row=3, column=1, sticky='w',
                                                 pady=(6, 0))
        header.columnconfigure(1, weight=1)

    def _make_thumbnail(self, parent) -> ttk.Label:
        try:
            with Image.open(self.filepath) as img:
                # Fast partial decode for large JPEGs before thumbnailing.
                img.draft(None, THUMBNAIL_MAX_SIZE)
                img.thumbnail(THUMBNAIL_MAX_SIZE)
                self._thumbnail = ImageTk.PhotoImage(img)  # keep a reference
            return ttk.Label(parent, image=self._thumbnail, relief='solid',
                             borderwidth=1)
        except OSError:
            return ttk.Label(parent, text='(no preview)',
                             foreground=self.muted_color)

    def _is_optimized(self) -> bool:
        return (self.task is not None
                and self.task.status == OPTIMIZED
                and self.task.final_filesize > 0)

    def _mount_savings_bar(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent)
        width, height = SAVINGS_BAR_SIZE
        final_ratio = self.task.final_filesize / self.task.original_filesize
        track = tk.Frame(frame, width=width, height=height,
                         background='#DDDDDD')
        track.pack_propagate(False)
        fill = tk.Frame(track, background='#2E9E5B')
        fill.place(relx=0, rely=0, relheight=1,
                   relwidth=min(max(final_ratio, 0.0), 1.0))
        track.pack(anchor='w')
        caption = (f'{human(self.task.final_filesize)} of '
                   f'{human(self.task.original_filesize)} · '
                   f'{self.task.percent_saved:.1f}% smaller')
        ttk.Label(frame, text=caption, foreground=self.muted_color) \
            .pack(anchor='w', pady=(3, 0))
        return frame

    # -- Body (single view; nothing is unmapped) ----------------------
    def _build_body(self):
        body = ttk.Frame(self.window, padding=(12, 6, 12, 12))
        body.pack(fill='both', expand=True)

        details = ttk.Frame(body)
        details.pack(fill='x', anchor='w')
        row = 0
        if self._is_optimized():
            row = self._add_section(details, row, 'Optimization',
                                    self._optimization_rows())
        self._add_section(details, row, 'Image properties',
                          self.info.properties, columns=2)
        details.columnconfigure(5, weight=1)   # absorb slack; keep left-aligned

        self._build_exif(body)

    def _optimization_rows(self):
        rows = {
            'Original size': human(self.task.original_filesize),
            'Final size': human(self.task.final_filesize),
            'Saved': (f'{human(self.task.bytes_saved)} '
                      f'({self.task.percent_saved:.1f}%)'),
        }
        if self.task.was_downsized:
            rows['Downsized'] = 'yes'
        if self.task.was_converted:
            rows['Converted'] = f'{self.task.orig_format} \u2192 ' \
                                f'{self.task.result_format}'
        return rows

    def _add_section(self, parent, row, title, rows, columns=1):
        ttk.Label(parent, text=title, font=self.bold_font) \
            .grid(row=row, column=0, columnspan=6, sticky='w',
                  pady=(0 if row == 0 else 12, 4))
        row += 1
        items = list(rows.items())
        # Flow into two balanced columns (column-major) when asked and worth
        # it, so tall sections use the empty horizontal space instead of
        # stretching the window downwards.
        if columns == 2 and len(items) > 4:
            parent.columnconfigure(2, minsize=28)   # gap between the columns
            half = (len(items) + 1) // 2
            blocks = (items[:half], items[half:])
            for line in range(half):
                for block_index, block in enumerate(blocks):
                    if line >= len(block):
                        continue
                    label, value = block[line]
                    base = block_index * 3   # left -> 0/1, right -> 3/4
                    self._kv_row(parent, row + line, base, label, value)
            return row + half
        for line, (label, value) in enumerate(items):
            self._kv_row(parent, row + line, 0, label, value)
        return row + len(items)

    def _kv_row(self, parent, row, base_column, label, value):
        ttk.Label(parent, text=label, foreground=self.muted_color) \
            .grid(row=row, column=base_column, sticky='w', padx=(0, 18),
                  pady=1)
        ttk.Label(parent, text=value) \
            .grid(row=row, column=base_column + 1, sticky='w', pady=1)

    def _build_exif(self, parent):
        ttk.Label(parent, text='EXIF', font=self.bold_font) \
            .pack(anchor='w', pady=(12, 4))
        if not self.info.exif:
            ttk.Label(parent, text='This image has no EXIF metadata.',
                      foreground=self.muted_color).pack(anchor='w')
            return

        holder = ttk.Frame(parent)
        holder.pack(fill='both', expand=True)
        tree = ttk.Treeview(holder, columns=('value',),
                            show='tree headings', height=9)
        tree.heading('#0', text='Tag', anchor='w')
        tree.heading('value', text='Value', anchor='w')
        tree.column('#0', width=200, stretch=False)
        tree.column('value', width=260)
        for section_title, tags in self.info.exif.items():
            section_id = tree.insert('', 'end', text=section_title, open=True)
            for tag_name, value in tags.items():
                tree.insert(section_id, 'end', text=tag_name, values=(value,))
        scrollbar = ttk.Scrollbar(holder, orient='vertical',
                                  command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')