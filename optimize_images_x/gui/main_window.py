import os
import tkinter as tk
import webbrowser
from collections import Iterable
from tkinter import ttk
from tkinter.filedialog import askopenfilenames, askdirectory

from optimize_images_x.global_setup import MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT, APP_NAME, DEFAULT_PATH, SUPPORTED_TYPES, \
    SUPPORTED_FORMATS
from optimize_images_x.global_setup import MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT
from optimize_images_x.gui.about_window import AboutWindow, ThanksWindow
from optimize_images_x.gui.base_app import BaseApp
from optimize_images_x.gui.settings_window import SettingsWindow


class App(BaseApp):
    def __init__(self, master, app_status, app_settings, task_settings, **kwargs):
        super().__init__(master, **kwargs)

        self.menu = tk.Menu(self.master)
        self.MenuFicheiro = tk.Menu(
            self.menu, postcommand=None)

        self.master = master
        self.app_status = app_status
        self.app_settings = app_settings
        self.task_settings = task_settings

        self.master.minsize(MAIN_MIN_WIDTH, MAIN_MIN_HEIGHT)
        self.master.maxsize(MAIN_MAX_WIDTH, MAIN_MAX_HEIGHT)

        self.gerar_menu()
        self.montar_barra_de_ferramentas()
        self.montar_tabela()
        self.compose_frames()

    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.select_item)

    def unbind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', None)

    def select_item(self, *event):
        """
        Obter img selecionada (após clique de rato na linha correspondente)
        """
        current_item = self.tree.focus()
        tree_row = self.tree.item(current_item)
        filepath = tree_row["values"][5]
        self.my_statusbar.set(f"{filepath}")

    def montar_tabela(self):
        self.tree['columns'] = ('', 'File', 'Converted', 'Size', '% Saved', 'Path')
        # self.tree.pack(side='top', expand=True, fill='both')
        self.tree.column('#0', anchor='w', minwidth=0, stretch=0, width=0)

        self.tree.column('', anchor='e', minwidth=46, stretch=0, width=46)
        self.tree.column('File', minwidth=40, stretch=1, width=120)
        self.tree.column('Converted', minwidth=40, stretch=1, width=160)
        self.tree.column('Size', minwidth=40, stretch=1, width=195)
        self.tree.column('% Saved', minwidth=40, stretch=1, width=150)
        # self.tree.column('Path', minwidth=0, stretch=0, width=0)

        self.tree["displaycolumns"] = ('', 'File', 'Converted', 'Size', '% Saved')

        self.configurar_tree()
        self.leftframe.grid_columnconfigure(0, weight=1)
        self.leftframe.grid_columnconfigure(1, weight=0)
        self.leftframe.grid_rowconfigure(0, weight=1)

        self.bind_tree()

    def montar_barra_de_ferramentas(self):
        self.btn_add = ttk.Button(self.topframe, text="➕", width=6,
                                  command=self.select_files)
        self.btn_add.grid(column=0, row=0)
        # self.dicas.bind(self.btn_add, 'Criar novo processo de reparação. (⌘N)')
        self.label_add = ttk.Label(
            self.topframe, font=self.btnFont, foreground=self.btnTxtColor, text="Nova reparação")
        self.label_add.grid(column=0, row=1)

        self.btn_detalhes = ttk.Button(self.topframe, text=" ℹ️️", width=3,
                                       command=lambda: self.create_window_detalhe_rep(
                                           num_reparacao=self.reparacao_selecionada))
        self.btn_detalhes.grid(column=6, row=0)
        ttk.Label(self.topframe, font=self.btnFont,
                  foreground=self.btnTxtColor, text="Detalhes").grid(column=6, row=1)
        # self.dicas.bind(
        #     self.btn_detalhes, 'Apresentar detalhes do processo\nde reparação selecionado. (⌘I)')

        self.btn_remessas = ttk.Button(
            self.topframe, text=" ⬆️️", width=3, command=self.create_window_settings)
        self.label_remessas = ttk.Label(
            self.topframe, font=self.btnFont, foreground=self.btnTxtColor, text="Remessas")
        self.btn_remessas.grid(row=0, column=15)
        self.label_remessas.grid(column=15, row=1)
        # self.dicas.bind(self.btn_remessas,
        #                'Mostrar/ocultar a janela de remessas. (⌘3)')

        for col in range(1, 16):
            self.topframe.columnconfigure(col, weight=0)
        # self.topframe.columnconfigure(3, weight=1)
        self.topframe.columnconfigure(5, weight=1)
        self.topframe.columnconfigure(11, weight=1)

    def create_window_settings(self, *event, criar_nova_remessa=None):
        if self.app_status.is_settings_window_open:
            # bring to front/focus
            pass
        else:
            self.app_status.settings_window = tk.Toplevel(self.master)
            self.settings_window = SettingsWindow(
                self.app_status.settings_window, self.app_status)
            self.app_status.is_settings_window_open = True
            self.app_status.janela_remessas.wm_protocol(
                "WM_DELETE_WINDOW", self.close_window_settings)

    def close_window_settings(self, *event):
        self.master.update_idletasks()
        self.app_status.is_settings_window_open = False
        self.app_status.settings_window.destroy()

    def gerar_menu(self):
        # Menu da janela principal
        self.master.config(menu=self.menu)

        self.menu.add_cascade(label="File", menu=self.MenuFicheiro)
        self.MenuFicheiro.add_command(
            label="Select files to process",
            command=self.select_files,
            accelerator="Command+o")
        self.MenuFicheiro.add_command(
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
            label="About " + APP_NAME, command=AboutWindow)
        self.helpmenu.add_command(
            label="Credits & Thanks", command=ThanksWindow)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Visit the developer's website",
                                  command=lambda: webbrowser.open(
                                      "https://no-title.victordomingos.com?s=oix", new=1, autoraise=True))
        # self.master.createcommand('::tk::mac::ShowPreferences', prefs_function)
        # self.master.bind('<<about-idle>>', about_dialog)
        # self.master.bind('<<open-config-dialog>>', config_dialog)
        self.master.createcommand('tkAboutDialog', AboutWindow)

    def atualizar_lista(self):
        """ Atualizar a lista de reparações na tabela principal.
        """
        for i in self.tree.get_children():  # Limpar tabela primeiro
            self.tree.delete(i)

        self.master.update()

        for task in self.app_status.tasks:
            values = ('', task.filename, task.status, task.orig_file_size_h,
                      '', task.filepath)
            self.tree.insert("", index="end", values=values)

        self.alternar_cores(self.tree)
        self.my_statusbar.show_progress(self.app_status.tasks_count,
                                        self.app_status.processed_tasks_count)

    def select_files(self):
        if not (folder := self.app_settings.last_opened_dir):
            folder = DEFAULT_PATH

        filepaths = askopenfilenames(parent=self,
                                     title='Choose file(s)',
                                     initialdir=folder,
                                     multiple=True,
                                     filetypes=SUPPORTED_TYPES)

        for filepath in filepaths:
            self.app_status.add_task(filepath)

        self.after_idle(self.atualizar_lista)

    def select_folder(self):
        if not (folder := self.app_settings.last_opened_dir):
            folder = DEFAULT_PATH

        path = askdirectory(parent=self,
                            title='Choose folder',
                            initialdir=folder,
                            mustexist=True)

        self.add_folder(path, self.task_settings.recurse_subfolders)
        self.after_idle(self.atualizar_lista)

    def add_folder(self, path, recursive: bool):
        n = 0
        for filepath in self.search_images(path, recursive):
            self.app_status.add_task(filepath)
            n += 1
            if n % 50 == 0:
                self.after_idle(lambda: self.atualizar_lista())

        self.after_idle(lambda: self.atualizar_lista())

    @staticmethod
    def search_images(dirpath: str, recursive: bool) -> Iterable[str]:
        if recursive:
            for root, _, files in os.walk(dirpath):
                for filename in files:
                    if not os.path.isfile(os.path.join(root, filename)):
                        continue
                    extension = os.path.splitext(filename)[1][1:]
                    if extension.lower() in SUPPORTED_FORMATS:
                        yield os.path.join(root, filename)
        else:
            with os.scandir(dirpath) as directory:
                for dir_entry in directory:
                    if not os.path.isfile(os.path.normpath(dir_entry)):
                        continue
                    extension = os.path.splitext(dir_entry)[1][1:]
                    if extension.lower() in SUPPORTED_FORMATS:
                        yield os.path.normpath(dir_entry)
