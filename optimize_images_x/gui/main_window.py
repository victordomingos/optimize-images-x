import concurrent.futures
import os
import tkinter as tk
import webbrowser
from timeit import default_timer as timer
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilenames, askdirectory

from optimize_images.data_structures import TaskResult
from optimize_images.do_optimization import do_optimization

from optimize_images_x.calcs import calc_percent_saved, get_percent_str, human
from optimize_images_x.db.app_settings import AppSettings
from optimize_images_x.db.app_stats import AppStats
from optimize_images_x.db.task_settings import TaskSettings
from optimize_images_x.global_setup import APP_NAME, DEFAULT_PATH
from optimize_images_x.global_setup import MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT
from optimize_images_x.global_setup import MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT
from optimize_images_x.global_setup import SUPPORTED_TYPES, PENDING
from optimize_images_x.gui.about_window import AboutWindow, ThanksWindow
from optimize_images_x.gui.app_status import AppStatus
from optimize_images_x.gui.base_app import BaseApp
from optimize_images_x.gui.settings_window import SettingsWindow
from optimize_images_x.task_conversion import get_task_icon, convert_task
from optimize_images_x.watch import watch_for_new_files, stop_watching


class App(BaseApp):
    def __init__(self, master, app_status, app_settings, task_settings,
                 app_stats, **kwargs):
        super().__init__(master, **kwargs)

        self.menu = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu, postcommand=None)

        self.master = master
        self.app_status: AppStatus = app_status
        self.app_settings: AppSettings = app_settings
        self.task_settings: TaskSettings = task_settings
        self.app_stats: AppStats = app_stats

        self.master.minsize(MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT)
        self.master.maxsize(MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT)

        self.observer = None
        self.event_handler = None

        self.generate_menu()
        self.generate_toolbar()
        self.mount_table()
        self.compose_frames()
        x = self.app_settings.main_window_x
        y = self.app_settings.main_window_y
        width = self.app_settings.main_window_w
        height = self.app_settings.main_window_h
        self.master.geometry(f"{width}x{height}+{x}+{y}")
        self.master.deiconify()
        self.master.update()
        self.after_idle(self.show_message)
        self.clear_list()

    def update_window_status(self, event):
        self.app_settings.main_window_x = self.master.winfo_x()
        self.app_settings.main_window_y = self.master.winfo_y()
        self.app_settings.main_window_w = self.master.winfo_width()
        self.app_settings.main_window_h = self.master.winfo_height()
        self.app_settings.save()

    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.select_item)

    def unbind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', None)

    def select_item(self, *event):
        """
            Display selected image path in status bar after clicking on a
            table row.
        """
        click_coords = (self.tree.winfo_pointerx() - self.tree.winfo_rootx(),
                        self.tree.winfo_pointery() - self.tree.winfo_rooty())
        filepath = self.tree.identify('item', *click_coords)
        self.my_statusbar.set(f"{filepath}")
        self.after(4000, self.update_count)

    def mount_table(self):
        self.tree['columns'] = ('', 'File', 'Original Size',
                                'New Size', '% Saved')

        self.tree.column('#0', anchor='w', minwidth=0, stretch=0, width=0)

        self.tree.column('', anchor='w', minwidth=30, stretch=0, width=30)
        self.tree.column('File', minwidth=150, stretch=1, width=200)
        self.tree.column('Original Size', anchor='e', minwidth=90, stretch=0, width=90)
        self.tree.column('New Size', anchor='e', minwidth=90, stretch=0, width=90)
        self.tree.column('% Saved', anchor='e', minwidth=60, stretch=0, width=70)

        self.tree["displaycolumns"] = ('', 'File', 'Original Size',
                                       'New Size', '% Saved')
        self.configure_tree()
        self.leftframe.grid_columnconfigure(0, weight=1)
        self.leftframe.grid_columnconfigure(1, weight=0)
        self.leftframe.grid_rowconfigure(0, weight=1)

        self.bind_tree()

    def generate_toolbar(self):
        os.chdir(os.path.dirname(__file__))
        icon_folder = os.getcwd() + "/../images/icons/"

        tool_icons = {
            'add_files': tk.PhotoImage(file=f'{icon_folder}file-plus.png'),
            'add_folder': tk.PhotoImage(file=f'{icon_folder}folder-plus.png'),
            'clear_clist': tk.PhotoImage(file=f'{icon_folder}delete.png'),
            'watch_folder': tk.PhotoImage(file=f'{icon_folder}eye.png'),
            'settings': tk.PhotoImage(file=f'{icon_folder}settings.png')
        }

        self.add_files_icon = tool_icons["add_files"]
        self.btn_add_files = ttk.Button(self.topframe,
                                        image=self.add_files_icon,
                                        text='Add files…',
                                        compound=tk.TOP,
                                        command=self.select_files)

        self.add_folder_icon = tool_icons["add_folder"]
        self.btn_add_folder = ttk.Button(self.topframe,
                                         image=self.add_folder_icon,
                                         text="Add folder…",
                                         compound=tk.TOP,
                                         command=self.select_folder)

        self.clear_icon = tool_icons["clear_clist"]
        self.btn_clear_queue = ttk.Button(self.topframe,
                                          image=self.clear_icon,
                                          text="Clear list",
                                          compound=tk.TOP,
                                          command=self.clear_list)

        self.watch_folder_icon = tool_icons["watch_folder"]
        self.btn_watch_folder = ttk.Button(self.topframe,
                                           image=self.watch_folder_icon,
                                           text="Watch folder…",
                                           compound=tk.TOP,
                                           command=self.select_folder_to_watch)

        self.settings_icon = tool_icons["settings"]
        self.btn_settings = ttk.Button(self.topframe,
                                       image=self.settings_icon,
                                       text="Settings",
                                       compound=tk.TOP,
                                       command=self.create_window_settings)

        # self.dicas.bind(self.btn_add_files, 'tooltip text. (⌘N)')

        self.btn_add_files.grid(column=0, row=0, ipady=4)
        self.btn_add_folder.grid(column=1, row=0, ipady=4)
        self.btn_clear_queue.grid(column=2, row=0, ipady=4)
        self.btn_watch_folder.grid(row=0, column=14, ipady=4)
        self.btn_settings.grid(row=0, column=15, ipady=4)  # last button
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
                self.task_settings)
            self.app_status.is_settings_window_open = True
            self.app_status.settings_window.wm_protocol(
                "WM_DELETE_WINDOW", self.close_window_settings)

    def close_window_settings(self, *event):
        self.master.update_idletasks()
        self.app_status.is_settings_window_open = False
        self.app_status.settings_window.destroy()

    def generate_menu(self):
        self.master.config(menu=self.menu)

        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Select files to process",
            command=self.select_files,
            accelerator="Command+o")
        self.file_menu.add_command(
            label="Select folder to process",
            command=self.select_folder,
            accelerator="Command+f")

        # self.menuVis = tk.Menu(self.menu)
        # self.menu.add_cascade(label="View", menu=self.menuVis)

        self.windowmenu = tk.Menu(self.menu, name='window')
        self.menu.add_cascade(menu=self.windowmenu, label='Window')
        self.windowmenu.add_separator()

        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
        #       helpmenu.add_command(label="Preferências", command=About)
        self.helpmenu.add_command(
            label="About " + APP_NAME, command=lambda: AboutWindow(self.app_stats))
        self.helpmenu.add_command(
            label="Credits & Thanks", command=ThanksWindow)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Visit the developer's website",
                                  command=lambda: webbrowser.open(
                                      "https://no-title.victordomingos.com?s=oix", new=1, autoraise=True))
        # self.master.createcommand('::tk::mac::ShowPreferences', prefs_function)
        # self.master.bind('<<about-idle>>', about_dialog)
        # self.master.bind('<<open-config-dialog>>', config_dialog)
        self.master.createcommand('tkAboutDialog', lambda: AboutWindow(self.app_stats))

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
        if self.app_status.processed_tasks_count:
            self.after_idle(self.update_report)
        else:
            self.after_idle(self.update_count)

    def select_files(self):
        if not (folder := self.app_settings.last_opened_dir):
            folder = DEFAULT_PATH

        filepaths = askopenfilenames(parent=self,
                                     title='Choose file(s)',
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
        if not (folder := self.app_settings.last_opened_dir):
            folder = DEFAULT_PATH

        path = askdirectory(parent=self,
                            title='Choose folder',
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
        if not (folder := self.app_settings.last_opened_dir):
            folder = DEFAULT_PATH

        path = askdirectory(parent=self,
                            title='Choose folder',
                            initialdir=folder,
                            mustexist=True)

        if not path:
            return

        self.app_settings.last_opened_dir = path
        self.app_settings.save()

        # self.watch_folder_icon = tool_icons["watch_folder"]
        self.btn_watch_folder.configure(text="Stop watching",
                                        command=self.stop_watching_folder)

        self.observer, self.event_handler = watch_for_new_files(path, self.task_settings, self)


    def stop_watching_folder(self):
        stop_watching(self.observer)
        self.btn_watch_folder.configure(text="Watch folder…",
                                        command=self.select_folder_to_watch)

    def clear_list(self):
        self.app_status.clear_list()
        self.update_img_list()
        self.my_statusbar.hide_progress()
        msg = 'Add image files or folders to start optimizing. ' \
              'Original files will be replaced (always work on copies).'
        self.my_statusbar.set(msg)

    def optimize_images(self):
        workers = self.task_settings.n_jobs
        tasks = (convert_task(t, self.task_settings)
                 for t in self.app_status.tasks
                 if t.status == PENDING)

        n_tasks = self.app_status.tasks_count
        n_files = 0

        self.my_statusbar.show_progress(n_tasks, 0,
                                        length=125,
                                        mode='determinate')

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            current_img = ''
            n_optimized_files = 0
            start_time = timer()
            weights_processed = []
            weights_saved = []
            optimized_paths = []
            result: TaskResult

            try:
                for result in executor.map(do_optimization, tasks):
                    current_img = result.img
                    n_files += 1

                    if result.was_optimized:
                        n_optimized_files += 1
                        weights_processed.append(result.orig_size)
                        weights_saved.append(result.orig_size - result.final_size)
                        optimized_paths.append(result.img)

                    self.app_status.update_task(result)
                    self.update_row(result)
                    self.my_statusbar.progress_update(n_files)
                    self.my_statusbar.set(f'{n_files}/{n_tasks} processed')
                    self.update()
            except concurrent.futures.process.BrokenProcessPool as bppex:
                print(bppex, current_img)

        processing_time = timer() - start_time

        self.app_stats.update_process_stats(n_optimized_files,
                                            processing_time,
                                            sum(weights_processed),
                                            sum(weights_saved))

        self.my_statusbar.hide_progress(last_update=n_tasks)
        self.update_report()

    def update_row(self, result: TaskResult):
        percent_saved = calc_percent_saved(result)
        percent_str = get_percent_str(percent_saved)

        values = (get_task_icon(result),
                  os.path.basename(result.img),
                  human(result.orig_size),
                  human(result.final_size),
                  percent_str)

        self.tree.item(result.img, values=values)

    def update_count(self):
        n_files = self.app_status.tasks_count
        total_weight = human(self.app_status.tasks_total_filesize)
        saved = ''
        if self.app_status.tasks_total_bytes_saved != 0:
            h_bytes = human(self.app_status.tasks_total_bytes_saved)
            percent = self.app_status.tasks_total_percent_saved
            saved = f' Saved {h_bytes} ({percent:.1f}%)'
        self.my_statusbar.set(f'{n_files} files, {total_weight} total{saved}')

    def update_report(self):
        if self.app_status.processed_tasks_count == 0:
            self.my_statusbar.set('No files were changed.')
            return

        processed = self.app_status.processed_tasks_count
        n_tasks = self.app_status.tasks_count
        saved = human(self.app_status.tasks_total_bytes_saved)
        orig_size = human(self.app_status.tasks_total_filesize)
        percent = self.app_status.tasks_total_percent_saved
        avg = human(self.app_status.tasks_total_bytes_saved / processed)

        msg = f'Optimized {processed}/{n_tasks} images. ' \
              f'Saved: {saved} of {orig_size} ({percent:.1f}%), avg. {avg} per file.'
        self.my_statusbar.set(msg)
        self.update_idletasks()

    def show_message(self):
        if self.app_settings.show_welcome_msg:
            msg = 'Please notice that all image optimizations are applied ' \
                  'destructivelly to the provided files. Always work on copies, ' \
                  'not on original image files.\n\n' \
                  'Do you want to receive this warning next time?'

            answer = messagebox.askyesno(title='Welcome to Optimize Images!',
                                         message=msg,
                                         parent=self)

            self.app_settings.show_welcome_msg = answer
            self.app_settings.save()
