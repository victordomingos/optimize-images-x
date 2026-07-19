import concurrent.futures
import math
import os
import platform
import subprocess
import threading
import tkinter as tk
import webbrowser
from functools import partial
from queue import Queue, Empty
from timeit import default_timer as timer
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilenames, askdirectory

import optimize_images_x.i18n as i18n
from optimize_images.api import PublicTaskResult
from optimize_images.api import optimize_single_image
from optimize_images_x.calcs import calc_percent_saved, get_percent_str, human
from optimize_images_x.db.app_settings import AppSettings
from optimize_images_x.db.app_stats import AppStats
from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.file_handling import open_in_default_viewer
from optimize_images_x.global_setup import APP_NAME, DEFAULT_PATH, OPTIMIZED, SKIPPED
from optimize_images_x.global_setup import MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT
from optimize_images_x.global_setup import MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT
from optimize_images_x.global_setup import SUPPORTED_TYPES, PENDING
from optimize_images_x.global_setup import resource_path
from optimize_images_x.gui.about_window import AboutWindow, ThanksWindow
from optimize_images_x.gui.app_status import AppStatus
from optimize_images_x.gui.base_app import BaseApp
from optimize_images_x.gui.extra_tk_utilities.tooltips import add_tooltip
from optimize_images_x.gui.image_info_window import ImageInfoWindow
from optimize_images_x.gui.settings_window import SettingsWindow
from optimize_images_x.search_images import is_image
from optimize_images_x.task_conversion import build_options, resolve_path
from optimize_images_x.task_conversion import get_task_icon
from optimize_images_x.watch import OptimizeImageEventHandler
from watchdog.observers import Observer

try:
    from tkinterdnd2 import DND_FILES

    DND_AVAILABLE = True
except ImportError:
    DND_FILES = None
    DND_AVAILABLE = False


class App(BaseApp):
    def __init__(self, master, app_status, app_settings, task_settings,
                 app_stats, **kwargs):
        super().__init__(master, **kwargs)
        self.watch_handler = OptimizeImageEventHandler(self)
        self.watch_queue = Queue()
        self.batch_queue = Queue()
        self.batch_done = threading.Event()
        self.batch_processed = 0
        self.batch_n_tasks = 0
        self.batch_errors = 0
        self.batch_summary = (0, 0.0, 0, 0)
        self.observer = None
        self.watch_stop = None
        self.watch_worker = None

        self.master = master

        # Apply saved language
        saved_lang = getattr(app_settings, 'language', None) or 'en'
        i18n.change_language(saved_lang)

        if platform.system() == 'Darwin':
            pass  # no configure — let Aqua paint the native, mode-aware background
        else:
            self.master.configure(background='grey95')

        self.master.title(i18n._("Optimize Images X"))

        self.gui_style = ttk.Style()
        self.gui_style.configure('Treeview.Heading',
                                 font=('-apple-system', 11))

        self.app_status: AppStatus = app_status
        self.app_settings: AppSettings = app_settings
        self.task_settings: TaskSettings = task_settings
        self.app_stats: AppStats = app_stats

        self.master.minsize(MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT)
        self.master.maxsize(MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT)

        self.generate_menu()
        self.generate_toolbar()
        self.mount_table()
        self.compose_frames()

        x = self.app_settings.main_window_x
        y = self.app_settings.main_window_y
        width = self.app_settings.main_window_w
        height = self.app_settings.main_window_h
        self.master.geometry(f"{width}x{height}+{x}+{y}")

        self.paths_to_ignore = []

        self.master.deiconify()
        self.master.update()
        self.clear_list()

        self.after_idle(self.show_welcome_msg)
        self.apply_main_bindings()
        self.start_appearance_watch()
        self.apply_dnd()

    def apply_main_bindings(self):
        self.master.bind_all("<Mod2-q>", self.shutdown)
        if platform.system() == 'Darwin':
            # On aqua, 'Command' is the reliable modifier name; menu
            # accelerator strings alone do not create working bindings.
            self.master.bind_all("<Command-i>", self.show_info)
        else:
            self.master.bind_all("<Control-i>", self.show_info)
        self.master.bind("<Configure>", self.update_window_status)

    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        self.tree.bind('<Return>', self.show_img)
        self.tree.bind('<Double-1>', self.show_img)
        if platform.system() == 'Darwin':
            self.tree.bind('<space>', self.quicklook)
            # Finder-style "open" shortcut, as an alias of Return.
            self.tree.bind('<Command-Down>', self.show_img)

    def shutdown(self, event):
        if self.observer is not None:
            self.stop_watching_folder()
        self.quit()

    def update_window_status(self, event):
        self.app_settings.main_window_x = self.master.winfo_x()
        self.app_settings.main_window_y = self.master.winfo_y()
        self.app_settings.main_window_w = self.master.winfo_width()
        self.app_settings.main_window_h = self.master.winfo_height()
        self.app_settings.save()

    def select_item(self, *event):
        """
            Display selected image path in status bar after clicking on a
            table row.
        """
        filepath = self.get_selected_img_path()
        self.my_statusbar.set(f"{filepath}")
        self.after(4000, self.update_count)

    def show_img(self, *event):
        """
            Display selected image in the system's default image viewer.
        """
        filepath = self.get_selected_img_path()
        if not filepath:
            return
        open_in_default_viewer(filepath)

    def quicklook(self, *event):
        filepath = self.get_selected_img_path()
        if not filepath:
            return
        subprocess.run(['qlmanage', '-p', filepath])

    def show_info(self, *event):
        """
            Open a window with detailed information (properties, optimization
            results and EXIF) about the selected image.
        """
        filepath = self.get_selected_img_path()
        if not filepath:
            self.my_statusbar.set('Please select an image first.')
            return
        task = next((t for t in self.app_status.tasks
                     if t.filepath == filepath), None)
        try:
            ImageInfoWindow.show(self.master, filepath, task)
        except OSError as error:
            messagebox.showerror(i18n._('Image info'),
                                 f'Could not read image:\n{error}')

    def get_selected_img_path(self):
        selection = self.tree.selection()
        if selection:
            return selection[0]
        click_coords = (self.tree.winfo_pointerx() - self.tree.winfo_rootx(),
                        self.tree.winfo_pointery() - self.tree.winfo_rooty())
        filepath = self.tree.identify('item', *click_coords)
        return filepath

    def mount_table(self):
        self.tree['columns'] = ('icon', 'file', 'original_size',
                                'new_size', 'percent_saved')

        self.tree.column('#0', anchor='w', minwidth=0, stretch=0, width=0)

        self.tree.column('icon', anchor='w', minwidth=30, stretch=0, width=30)
        self.tree.column('file', minwidth=150, stretch=1, width=200)
        # Wide enough for the longer translated headings too (e.g. pt's
        # "Tamanho Original", "Novo Tamanho"), not just the English ones.
        self.tree.column('original_size', anchor='e', minwidth=100, stretch=0, width=130)
        self.tree.column('new_size', anchor='e', minwidth=90, stretch=0, width=120)
        self.tree.column('percent_saved', anchor='e', minwidth=70, stretch=0, width=90)

        self.tree["displaycolumns"] = ('icon', 'file', 'original_size',
                                       'new_size', 'percent_saved')
        self.configure_tree()
        self.leftframe.grid_columnconfigure(0, weight=1)
        self.leftframe.grid_columnconfigure(1, weight=0)
        self.leftframe.grid_rowconfigure(0, weight=1)

        self.bind_tree()

    def generate_toolbar(self):
        icon_folder = resource_path('images/icons')

        tool_icons = {
            'add_files': tk.PhotoImage(file=os.path.join(icon_folder, 'file-plus.png')),
            'add_folder': tk.PhotoImage(file=os.path.join(icon_folder, 'folder-plus.png')),
            'clear_clist': tk.PhotoImage(file=os.path.join(icon_folder, 'delete.png')),
            'watch_folder': tk.PhotoImage(file=os.path.join(icon_folder, 'eye.png')),
            'settings': tk.PhotoImage(file=os.path.join(icon_folder, 'settings.png'))
        }

        self.add_files_icon = tool_icons["add_files"]
        self.btn_add_files = ttk.Button(self.topframe,
                                        image=self.add_files_icon,
                                        text=i18n._('Add files…'),
                                        compound=tk.TOP,
                                        command=self.select_files,
                                        style='Toolbutton')
        self.btn_add_files._text_key = 'Add files…'
        self.btn_add_files._tooltip_key = 'Add image files to the list'

        self.add_folder_icon = tool_icons["add_folder"]
        self.btn_add_folder = ttk.Button(self.topframe,
                                         image=self.add_folder_icon,
                                         text=i18n._('Add folder…'),
                                         compound=tk.TOP,
                                         command=self.select_folder,
                                         style='Toolbutton')
        self.btn_add_folder._text_key = 'Add folder…'
        self.btn_add_folder._tooltip_key = 'Add all images from a folder'

        self.clear_icon = tool_icons["clear_clist"]
        self.btn_clear_queue = ttk.Button(self.topframe,
                                          image=self.clear_icon,
                                          text=i18n._('Clear list'),
                                          compound=tk.TOP,
                                          command=self.clear_list,
                                          style='Toolbutton')
        self.btn_clear_queue._text_key = 'Clear list'
        self.btn_clear_queue._tooltip_key = 'Remove every item from the list'

        self.watch_folder_icon = tool_icons["watch_folder"]
        self.btn_watch_folder = ttk.Button(self.topframe,
                                           image=self.watch_folder_icon,
                                           text=i18n._('Watch folder…'),
                                           compound=tk.TOP,
                                           command=self.select_folder_to_watch,
                                           style='Toolbutton')
        self.btn_watch_folder._text_key = 'Watch folder…'
        self.btn_watch_folder._tooltip_key = 'Watch a folder and optimize new images automatically'

        self.settings_icon = tool_icons["settings"]
        self.btn_settings = ttk.Button(self.topframe,
                                       image=self.settings_icon,
                                       text=i18n._('Settings'),
                                       compound=tk.TOP,
                                       command=self.create_window_settings,
                                       style='Toolbutton')
        self.btn_settings._text_key = 'Settings'
        self.btn_settings._tooltip_key = 'Open settings'

        # self.dicas.bind(self.btn_add_files, 'tooltip text. (⌘N)')

        self.btn_add_files.grid(column=0, row=0, ipady=4)
        self.btn_add_folder.grid(column=1, row=0, ipady=4)
        self.btn_clear_queue.grid(column=2, row=0, ipady=4)
        self.btn_watch_folder.grid(row=0, column=14, ipady=4)
        self.btn_settings.grid(row=0, column=15, ipady=4)  # last button

        self.btn_add_files._tooltip = add_tooltip(self.btn_add_files, i18n._('Add image files to the list'))
        self.btn_add_folder._tooltip = add_tooltip(self.btn_add_folder, i18n._('Add all images from a folder'))
        self.btn_clear_queue._tooltip = add_tooltip(self.btn_clear_queue, i18n._('Remove every item from the list'))
        self.btn_watch_folder._tooltip = add_tooltip(self.btn_watch_folder,
                                                     i18n._('Watch a folder and optimize new images automatically'))
        self.btn_settings._tooltip = add_tooltip(self.btn_settings, i18n._('Open settings'))
        # self.dicas.bind(self.btn_settings,
        #                'Mostrar/ocultar a janela de remessas. (⌘3)')

        for col in range(1, 16):
            self.topframe.columnconfigure(col, weight=0)

        self.topframe.columnconfigure(5, weight=1)  # auto-space at position 5

    def create_window_settings(self, *event):
        if self.app_status.is_settings_window_open:
            self.app_status.settings_window.lift()
        else:
            self.app_status.settings_window = tk.Toplevel(self.master)
            self.settings_window = SettingsWindow(
                self.app_status.settings_window,
                self.app_status,
                self.app_settings,
                self.task_settings,
                self)
            self.app_status.is_settings_window_open = True
            self.app_status.settings_window.wm_protocol(
                "WM_DELETE_WINDOW", self.close_window_settings)

    def close_window_settings(self, *event):
        self.master.update_idletasks()
        self.app_status.is_settings_window_open = False
        self.app_status.settings_window.destroy()

    def create_about_window(self, *event):
        """Open the About window, or raise it if already open."""
        existing = getattr(self, 'about_window', None)
        if existing is not None and existing.popupRoot.winfo_exists():
            existing.popupRoot.lift()
        else:
            self.about_window = AboutWindow(self.app_stats)

    def create_thanks_window(self, *event):
        """Open the Credits & Thanks window, or raise it if already open."""
        existing = getattr(self, 'thanks_window', None)
        if existing is not None and existing.thanksRoot.winfo_exists():
            existing.thanksRoot.lift()
        else:
            self.thanks_window = ThanksWindow()

    def generate_menu(self):
        # Rebuilt from scratch on every call (including language switches via
        # refresh_language()): destroying the previous top-level menu also
        # destroys its cascaded children (file_menu, window/tools menu, help
        # menu), since they were created with it as their parent. Re-using
        # the old widgets and only re-adding entries would instead pile up
        # duplicate menu items on each switch.
        if hasattr(self, 'menu'):
            self.menu.destroy()
        self.menu = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu, postcommand=None)

        self.master.config(menu=self.menu)

        self.menu.add_cascade(label=i18n._("File"), menu=self.file_menu)
        self.file_menu.add_command(
            label=i18n._("Select files to process…"),
            command=self.select_files,
            accelerator="Command+o")
        self.file_menu.add_command(
            label=i18n._("Select folder to process…"),
            command=self.select_folder,
            accelerator="Command+f")
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label=i18n._("Watch a folder for new files…"),
            command=self.select_folder_to_watch,
            accelerator="Command+Shift+F")
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label=i18n._("Open image"),
            command=self.show_img)
        if platform.system() == 'Darwin':
            self.file_menu.add_command(
                label=i18n._("Quick Look Preview"),
                command=self.quicklook,
                accelerator="Space")
        self.file_menu.add_command(
            label=i18n._("Show image info"),
            command=self.show_info,
            accelerator="Command+I" if platform.system() == 'Darwin'
            else "Control+I")

        # self.menuVis = tk.Menu(self.menu)
        # self.menu.add_cascade(label="View", menu=self.menuVis)

        if platform.system() == 'Darwin':
            self.windowmenu = tk.Menu(self.menu, name='window')
            self.menu.add_cascade(menu=self.windowmenu, label=i18n._('Window'))
            self.windowmenu.add_separator()
            self.master.createcommand('::tk::mac::ShowPreferences',
                                      self.create_window_settings)
        else:
            self.tools_menu = tk.Menu(self.menu, name='tools')
            self.menu.add_cascade(menu=self.tools_menu, label=i18n._('Tools'))
            self.tools_menu.add_command(label=i18n._("Settings"),
                                        command=self.create_window_settings,
                                        accelerator="Control+s")

        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label=i18n._("Help"), menu=self.helpmenu)
        self.helpmenu.add_command(label=i18n._("About ") + APP_NAME(),
                                  command=self.create_about_window)
        self.helpmenu.add_command(label=i18n._("Credits & Thanks"),
                                  command=self.create_thanks_window)
        self.helpmenu.add_separator()

        url = "https://no-title.victordomingos.com?s=oix"
        web_command = lambda: webbrowser.open(url, new=1, autoraise=True)
        self.helpmenu.add_command(label=i18n._("Visit the developer's website"),
                                  command=web_command)

        self.master.createcommand('tkAboutDialog', self.create_about_window)

    def update_img_list(self):
        """ Update the image list. """
        for i in self.tree.get_children():  # Limpar tabela primeiro
            self.tree.delete(i)

        for task in self.app_status.tasks:
            values = (get_task_icon(task),
                      task.filename,
                      task.orig_file_size_h,
                      task.final_file_size_h,
                      get_percent_str(task.percent_saved))

            self.tree.insert("", index="end", iid=task.filepath, values=values)

        self.alternate_colors(self.tree)
        self.update_drop_hint()
        if self.app_status.processed_tasks_count:
            self.after_idle(self.update_report)
        else:
            self.after_idle(self.update_count)

    def select_files(self):
        folder = self.app_settings.last_opened_dir
        if not folder:
            folder = DEFAULT_PATH

        filepaths = askopenfilenames(parent=self,
                                     title=i18n._("Choose file(s)"),
                                     initialdir=folder,
                                     multiple=True,
                                     filetypes=SUPPORTED_TYPES)
        if not filepaths:
            return

        # self.app_status.clear_list()
        added_imgs: int = 0
        added_bytes: int = 0
        for filepath in filepaths:
            added_imgs, added_bytes = self.app_status.add_task(filepath)

        if added_imgs:
            self.update_img_list()
            self.optimize_images()

        self.app_stats.update_load_stats(added_imgs, added_bytes)

    def select_folder(self):
        folder = self.app_settings.last_opened_dir
        if not folder:
            folder = DEFAULT_PATH

        path = askdirectory(parent=self,
                            title=i18n._("Choose folder"),
                            initialdir=folder,
                            mustexist=True)

        if not path:
            return

        # self.app_status.clear_list()
        self.app_settings.last_opened_dir = path
        self.app_settings.save()

        n_files, n_bytes = self.app_status.add_folder(
            path, self.task_settings.recurse_subfolders)

        if n_files:
            self.update_img_list()
            self.optimize_images()

        self.app_stats.update_load_stats(n_files, n_bytes)

    def select_folder_to_watch(self):
        self.show_watch_msg()

        folder = self.app_settings.last_opened_dir
        if not folder:
            folder = DEFAULT_PATH

        path = askdirectory(parent=self,
                            title=i18n._("Choose folder"),
                            initialdir=folder,
                            mustexist=True)

        if not path:
            return

        self.app_settings.last_opened_dir = path
        self.app_settings.save()

        # self.watch_folder_icon = tool_icons["watch_folder"]
        self.btn_watch_folder.configure(text=i18n._("Stop watching"),
                                        command=self.stop_watching_folder)

        self.my_statusbar.set(i18n._("Started watching folder for new files."))
        self.my_statusbar.show_progress()

        self.watch_stop = threading.Event()
        self.watch_worker = threading.Thread(target=self._watch_consumer,
                                             daemon=True)
        self.watch_worker.start()
        self.observer = Observer()
        self.observer.schedule(self.watch_handler, path, recursive=True)
        self.observer.start()

    def notify(self, event):
        """Forward events from watchdog to the consumer thread."""
        self.watch_queue.put(event)

    def _watch_consumer(self):
        """Processes queue events out of the main UI thread."""
        stop = self.watch_stop
        while not stop.is_set():
            try:
                watchdog_event = self.watch_queue.get(timeout=0.2)
            except Empty:
                continue

            is_dir = watchdog_event.is_directory
            is_not_img = not is_image(watchdog_event.src_path)
            is_in_ignore_list = watchdog_event.src_path in self.paths_to_ignore

            if is_dir or is_not_img or is_in_ignore_list:
                continue

            result, status, processing_time = \
                self._optimize_watched(watchdog_event)

            self.after_idle(self._on_watch_result,
                            result, status, processing_time)

    def _optimize_watched(self, watchdog_event):
        """Optimizes the detected file (runs on the processing thread)."""
        start_time = timer()
        img_path = watchdog_event.src_path
        self.paths_to_ignore.append(img_path)
        OptimizeImageEventHandler.wait_for_write_finish(img_path)
        result: PublicTaskResult = optimize_single_image(
            img_path, **build_options(self.task_settings))
        processing_time = timer() - start_time

        status = SKIPPED
        if result.was_optimized:
            status = OPTIMIZED
            same_format = result.result_format == result.orig_format
            convert_big = self.task_settings.convert_big_to_jpg
            convert_all = self.task_settings.convert_all_to_jpg

            # also ignore generated imgs of different format
            if (convert_big or convert_all) and not same_format:
                self.paths_to_ignore.append(result.img)

        return result, status, processing_time

    def _on_watch_result(self, result, status, processing_time):
        """Updates status and grid (runs on main thread)."""
        if result.was_optimized:
            weight_saved = result.orig_size - result.final_size
            self.app_stats.update_process_stats(1, processing_time,
                                                result.orig_size, weight_saved)

        imgs, bytes_ = self.app_status.add_task(result.img, status,
                                                result.orig_size,
                                                result.final_size)

        self.app_stats.update_load_stats(imgs, bytes_)
        self.insert_row(result)
        self.alternate_colors(self.tree)

    def stop_watching_folder(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        if self.watch_stop is not None:
            self.watch_stop.set()
            self.watch_stop = None
            self.watch_worker = None

        self.btn_watch_folder.configure(text=i18n._("Watch folder…"),
                                        command=self.select_folder_to_watch)

        self.my_statusbar.hide_progress()
        self.my_statusbar.set(i18n._("Stopped watching folder."))

    def apply_dnd(self):
        """Register or unregister the window as a drop target, per the setting."""
        if not DND_AVAILABLE:
            return

        if self.app_settings.enable_dnd:
            self.master.drop_target_register(DND_FILES)
            self.master.dnd_bind('<<Drop>>', self.handle_drop)
            self.master.dnd_bind('<<DropEnter>>', self._on_drag_enter)
            self.master.dnd_bind('<<DropLeave>>', self._on_drag_leave)
        else:
            try:
                self.master.drop_target_unregister()
            except Exception:
                pass
            self._end_drag_feedback()

        self.update_drop_hint()

    # ---- Empty-state drag-and-drop hint -------------------------------
    def _ensure_drop_hint(self):
        if getattr(self, 'drop_hint', None) is None:
            self.drop_hint = tk.Canvas(self.leftframe, width=340, height=200,
                                       highlightthickness=0, borderwidth=0,
                                       takefocus=0)

    def update_drop_hint(self, *event):
        """Show a centered hint over the empty list while drag-and-drop is
        available and enabled; hide it once the list has items or the feature
        is turned off."""
        self._ensure_drop_hint()
        show = (DND_AVAILABLE and self.app_settings.enable_dnd
                and not self.tree.get_children())
        if show:
            self._draw_drop_hint()
            self.drop_hint.place(in_=self.tree, relx=0.5, rely=0.5,
                                 anchor='center')
            self._raise_widget(self.drop_hint)
        else:
            self.drop_hint.place_forget()

    def _drop_hint_colors(self):
        """Background and muted foreground for the hint.

        On aqua, use dynamic system colours that adapt to light/dark on their
        own (resolved at draw time, and redrawn on appearance changes); other
        themes fall back to fixed colours chosen from the dark state.
        """
        if self.style.theme_use() == 'aqua':
            return 'systemTextBackgroundColor', 'systemPlaceholderTextColor'
        if self._is_dark():
            return '#1e1e1e', '#8a8f98'
        return '#ffffff', '#a2a8b0'

    @staticmethod
    def _rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
        """Draw a rounded rectangle outline as a smoothed (optionally dashed)
        line, since tk.Canvas has no native rounded-rectangle primitive."""
        points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r,
                  x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
                  x1, y1 + r, x1, y1, x1 + r, y1]
        return canvas.create_line(points, smooth=True, **kwargs)

    def _draw_drop_hint(self):
        canvas = self.drop_hint
        canvas.delete('all')
        bg, fg = self._drop_hint_colors()
        canvas.configure(background=bg)
        w, h = int(canvas['width']), int(canvas['height'])
        cx = w // 2

        # Subtle dashed rounded border marking the droppable area.
        self._rounded_rect(canvas, 8, 8, w - 8, h - 8, 28, fill=fg,
                           dash=(3, 4), width=1, capstyle='round')
        # Line-art icon: an arrow dropping into an open tray.
        canvas.create_line(cx, 44, cx, 92, fill=fg, width=2, capstyle='round')
        canvas.create_line(cx - 11, 80, cx, 92, cx + 11, 80, fill=fg, width=2,
                           capstyle='round', joinstyle='round')
        canvas.create_line(cx - 30, 98, cx - 30, 116, cx + 30, 116, cx + 30,
                           98, fill=fg, width=2, capstyle='round',
                           joinstyle='round')
        # Two lines of guidance.
        canvas.create_text(cx, h - 56,
                           text=i18n._('Drag and drop images or folders here'),
                           fill=fg, font=self.statusFont)
        canvas.create_text(cx, h - 33,
                           text=i18n._('or use Add files/Add folder above'),
                           fill=fg, font=self.btnFont)

    def refresh_appearance(self):
        super().refresh_appearance()
        self.update_drop_hint()

    # ---- Drag feedback (active drop highlight) -------------------------
    _RING_THICKNESS = 3

    def _ensure_drag_ring(self):
        if getattr(self, '_drag_ring', None) is None:
            self._drag_ring = [tk.Frame(self.leftframe, borderwidth=0,
                                        highlightthickness=0)
                               for _ in range(4)]
            self._drag_anim_id = None
            self._drag_phase = 0

    def _on_drag_enter(self, event=None):
        """Pointer with a payload entered the window: show active feedback."""
        self._start_drag_feedback()
        return getattr(event, 'action', None)

    def _on_drag_leave(self, event=None):
        """Pointer left without dropping: remove the feedback."""
        self._end_drag_feedback()

    def _start_drag_feedback(self):
        if not (DND_AVAILABLE and self.app_settings.enable_dnd):
            return
        self._ensure_drag_ring()
        t = self._RING_THICKNESS
        top, bottom, left, right = self._drag_ring
        top.place(in_=self.tree, relx=0, rely=0, relwidth=1, height=t,
                  anchor='nw')
        bottom.place(in_=self.tree, relx=0, rely=1.0, relwidth=1, height=t,
                     anchor='sw')
        left.place(in_=self.tree, relx=0, rely=0, relheight=1, width=t,
                   anchor='nw')
        right.place(in_=self.tree, relx=1.0, rely=0, relheight=1, width=t,
                    anchor='ne')
        for strip in self._drag_ring:
            self._raise_widget(strip)
        if self._drag_anim_id is None:
            self._pulse_drag_ring()

    def _end_drag_feedback(self, *event):
        if getattr(self, '_drag_anim_id', None) is not None:
            try:
                self.after_cancel(self._drag_anim_id)
            except Exception:
                pass
            self._drag_anim_id = None
        for strip in getattr(self, '_drag_ring', []) or []:
            strip.place_forget()

    def _pulse_drag_ring(self):
        """Animate the ring with a gentle blue glow while a drag is active."""
        self._drag_phase = (self._drag_phase + 1) % 24
        t = (math.sin(self._drag_phase / 24 * 2 * math.pi) + 1) / 2  # 0..1
        color = self._mix_hex('#2563eb', '#7db0ff', t)
        for strip in self._drag_ring:
            strip.configure(background=color)
        self._drag_anim_id = self.after(60, self._pulse_drag_ring)

    @staticmethod
    def _mix_hex(c1, c2, t):
        a = tuple(int(c1[i:i + 2], 16) for i in (1, 3, 5))
        b = tuple(int(c2[i:i + 2], 16) for i in (1, 3, 5))
        m = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
        return f'#{m[0]:02x}{m[1]:02x}{m[2]:02x}'

    @staticmethod
    def _raise_widget(widget):
        """Raise a widget in the window stacking order.

        Needed because tk.Canvas binds both ``lift`` and ``tkraise`` to its
        item-level ``tag_raise``, which fails when called with no item; this
        invokes the actual window-stacking 'raise' command instead.
        """
        widget.tk.call('raise', widget._w)

    @staticmethod
    def _parse_dropped_paths(data):
        """Split the <<Drop>> data string into individual filesystem paths."""
        paths = []
        token = ''
        in_braces = False
        for char in data:
            if char == '{':
                in_braces = True
            elif char == '}':
                in_braces = False
                paths.append(token)
                token = ''
            elif char == ' ' and not in_braces:
                if token:
                    paths.append(token)
                    token = ''
            else:
                token += char
        if token:
            paths.append(token)
        return paths

    def handle_drop(self, event):
        self._end_drag_feedback()
        if not (DND_AVAILABLE and self.app_settings.enable_dnd):
            return

        if self.app_settings.show_dnd_msg:
            if not self.show_dnd_msg():
                return

        recurse = self.task_settings.recurse_subfolders
        added_imgs = 0
        added_bytes = 0
        for path in self._parse_dropped_paths(event.data):
            if os.path.isdir(path):
                n_files, n_bytes = self.app_status.add_folder(path, recurse)
                added_imgs += n_files
                added_bytes += n_bytes
            elif os.path.isfile(path) and is_image(path):
                n_files, n_bytes = self.app_status.add_task(path)
                added_imgs += n_files
                added_bytes += n_bytes

        if added_imgs:
            self.update_img_list()
            self.optimize_images()

        self.app_stats.update_load_stats(added_imgs, added_bytes)

    def show_dnd_msg(self):
        """Confirm the destructive operation before the first drag-and-drop.

        Returns True if the user wants to proceed with the current drop.
        """
        proceed = messagebox.askokcancel(
            title=i18n._("Drag and drop"),
            message=i18n._('The dropped images will be optimized in place, replacing '
                           'the original files (always work on copies). Dropped '
                           'folders are scanned according to your "Recurse through '
                           'subfolders" setting.\n\nDo you want to proceed?'),
            parent=self)

        if not proceed:
            return False

        keep_warning = messagebox.askyesno(
            title=i18n._("Drag and drop"),
            message=i18n._('Do you want to see this warning next time?'),
            parent=self)

        self.app_settings.show_dnd_msg = keep_warning
        self.app_settings.save()
        return True

    def clear_list(self):
        self.app_status.clear_list()
        self.update_img_list()
        self.my_statusbar.hide_progress()
        msg = i18n._('Add image files or folders to start optimizing. ' \
                     'Original files will be replaced (always work on copies).')
        self.my_statusbar.set(msg)

    def optimize_images(self):
        opts = build_options(self.task_settings)
        paths = [resolve_path(t)
                 for t in self.app_status.tasks
                 if t.status == PENDING]

        if not paths:
            return

        n_tasks = self.app_status.tasks_count
        self.my_statusbar.show_progress(n_tasks, 0, 125, mode='determinate')

        # Make sure the pending rows are visible before work starts.
        self.update_idletasks()

        self.batch_queue = Queue()
        self.batch_done = threading.Event()
        self.batch_processed = 0
        self.batch_n_tasks = n_tasks
        self.batch_errors = 0

        worker = threading.Thread(target=self._run_batch,
                                  args=(opts, paths),
                                  daemon=True)
        worker.start()
        self.after(50, self._drain_batch_queue)

    def _run_batch(self, opts, paths):
        """Run the optimization pool off the main thread, queueing each result."""
        workers = self.task_settings.n_jobs
        optimize = partial(optimize_single_image, **opts)
        n_optimized_files = 0
        start_time = timer()
        weights_processed = 0
        weights_saved = 0
        current_img = ''

        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(optimize, path): path for path in paths}
                for future in concurrent.futures.as_completed(futures):
                    path = futures[future]
                    try:
                        result = future.result()
                    except Exception as ex:
                        self.batch_queue.put(('error', path, str(ex)))
                        continue
                    self.batch_queue.put(result)
        except concurrent.futures.process.BrokenProcessPool as bppex:
            print(bppex, current_img)

        processing_time = timer() - start_time
        self.batch_summary = (n_optimized_files, processing_time,
                              weights_processed, weights_saved)
        self.batch_done.set()

    def _drain_batch_queue(self):
        """Pull all available results, update their rows, and repaint once."""
        updated = False
        while True:
            try:
                item = self.batch_queue.get_nowait()
            except Empty:
                break

            if isinstance(item, tuple) and item[0] == 'error':
                tag, path, msg = item
                self.my_statusbar.set(i18n._('Error') + ': ' + msg + ' | ' + os.path.basename(path))
                self.batch_errors += 1
                continue

            updated = True
            self.batch_processed += 1
            try:
                self.app_status.update_task(item)
                self.update_row(item)
            except Exception as ex:
                print('Could not update row for', item.img, '-', ex)

        if updated:
            self.my_statusbar.progress_update(self.batch_processed)
            self.my_statusbar.set(
                i18n._(f'{self.batch_processed}/{self.batch_n_tasks} processed'))
            self.update()

        if self.batch_done.is_set() and self.batch_queue.empty():
            self._on_batch_done(*self.batch_summary, self.batch_n_tasks)
        else:
            self.after(50, self._drain_batch_queue)

    def _on_batch_done(self, n_optimized_files, processing_time,
                       weights_processed, weights_saved, n_tasks):
        """Finalize stats and report on the main thread when the batch ends."""
        self.app_stats.update_process_stats(n_optimized_files,
                                            processing_time,
                                            weights_processed,
                                            weights_saved)
        self.my_statusbar.hide_progress(last_update=n_tasks)
        self.update_report()

    def update_row(self, result: PublicTaskResult):
        percent_saved = calc_percent_saved(result)
        percent_str = get_percent_str(percent_saved)

        values = (get_task_icon(result),
                  os.path.basename(result.img),
                  human(result.orig_size),
                  human(result.final_size),
                  percent_str)

        try:
            self.tree.item(result.img, values=values)
        except tk.TclError:
            pass

    def insert_row(self, result: PublicTaskResult):
        percent_saved = calc_percent_saved(result)
        percent_str = get_percent_str(percent_saved)

        values = (get_task_icon(result),
                  os.path.basename(result.img),
                  human(result.orig_size),
                  human(result.final_size),
                  percent_str)

        self.tree.insert("", index="end", iid=result.img, values=values)

    def update_count(self):
        n_files = self.app_status.tasks_count
        total_weight = human(self.app_status.tasks_total_filesize)
        saved = ''
        if self.app_status.tasks_total_bytes_saved != 0:
            h_bytes = human(self.app_status.tasks_total_bytes_saved)
            percent = self.app_status.tasks_total_percent_saved
            saved = f' {i18n._("Saved")} {h_bytes} ({percent:.1f}%)'
        self.my_statusbar.set(f'{n_files} {i18n._("files")}, {total_weight} {i18n._("total")}{saved}')

    def update_report(self):
        if self.app_status.processed_tasks_count == 0:
            self.my_statusbar.set(i18n._('No files were changed.'))
            return

        processed = self.app_status.processed_tasks_count
        n_tasks = self.app_status.tasks_count
        saved = human(self.app_status.tasks_total_bytes_saved)
        orig_size = human(self.app_status.tasks_total_filesize)
        percent = self.app_status.tasks_total_percent_saved
        avg = human(self.app_status.tasks_total_bytes_saved / processed)

        msg = f'{i18n._("Optimized")} {processed}/{n_tasks} {i18n._("images")}. ' \
              f'{i18n._("Saved")}: {saved} {i18n._("of")} {orig_size} ({percent:.1f}%), {i18n._("avg.")} {avg} {i18n._("per file")}.'
        self.my_statusbar.set(msg)
        self.update_idletasks()

    def show_welcome_msg(self):
        if self.app_settings.show_welcome_msg == 1:
            msg1 = i18n._('Please notice that all image optimizations are applied ' \
                          'destructivelly to the provided files. Always work on copies, ' \
                          'not on original image files.\n\n' \
                          'Do you want to receive this warning next time?')

            answer1 = messagebox.askyesno(title=i18n._('Welcome to Optimize Images!'),
                                          message=msg1,
                                          parent=self)

            self.app_settings.show_welcome_msg = answer1
            self.app_settings.save()

    def show_watch_msg(self):
        if self.app_settings.show_watch_msg:
            msg2 = i18n._('Optimize Images will enter into Listening Mode, and watch ' \
                          'the selected folder for any new image files being created ' \
                          'until you press "Stop". After that moment, if a new image ' \
                          'file is created, it will be immediately processed.\n\n' \
                          'Do you want to receive this information next time?')

            answer2 = messagebox.askyesno(title=i18n._('Watching a folder for new image files'),
                                          message=msg2,
                                          parent=self)

            self.app_settings.show_watch_msg = answer2
            self.app_settings.save()

    def refresh_language(self):
        """Refresh all UI text to reflect the current language."""
        self.master.title(APP_NAME())

        self.generate_menu()

        for btn in [self.btn_add_files, self.btn_add_folder,
                    self.btn_clear_queue, self.btn_watch_folder,
                    self.btn_settings]:
            if hasattr(btn, '_text_key'):
                btn.config(text=i18n._(btn._text_key))
            if hasattr(btn, '_tooltip') and btn._tooltip is not None:
                btn._tooltip.set_text(i18n._(btn._tooltip_key))

        self.configure_tree()
        self.update_drop_hint()
        self.update_count()
        self.update_report()

        if hasattr(self, 'settings_window') and self.settings_window is not None:
            self.settings_window.refresh_language()

        about_window = getattr(self, 'about_window', None)
        if about_window is not None and about_window.popupRoot.winfo_exists():
            about_window.refresh_language()

        thanks_window = getattr(self, 'thanks_window', None)
        if thanks_window is not None and thanks_window.thanksRoot.winfo_exists():
            thanks_window.refresh_language()
