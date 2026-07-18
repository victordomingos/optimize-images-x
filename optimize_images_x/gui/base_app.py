import platform
import subprocess
import time
import tkinter as tk
import tkinter.font
from functools import lru_cache
from tkinter import ttk

import optimize_images_x.i18n as i18n
from optimize_images_x.global_setup import text_color, ui_font
from optimize_images_x.gui.extra_tk_utilities.auto_scrollbar import AutoScrollbar
from optimize_images_x.gui.extra_tk_utilities.status_bar import StatusBar


# import Pmw

@lru_cache(maxsize=10)
def is_numeric(string: str) -> bool:
    """
    test if a string s is numeric
    """
    for c in string:
        if c not in "1234567890.":
            return False

    return True


def change_numeric(data):
    """
    if the data to be sorted is numeric change to float
    """
    if not data:
        return []

    if is_numeric(data[0][0]):
        return [(float(child), col) for child, col in data]
    else:
        return data


class BaseApp(ttk.Frame):
    """
    Classe de base para as janelas de aplicação. Inclui uma estrutura de vários frames:
        - topframe (Barra de ferramentas)
        - centerframe (organizador da área central), composto por:
          - leftframe (que recebe a tabela principal tree)

        - bottomframe (área reservada à barra de estado)
        - tree (tabela com algumas predefinições, ordenação ao clicar nos
          cabeçalhos das colunas, scrollbar automática)
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.style = ttk.Style()

        # self.dicas = Pmw.Balloon(self.master, label_background='#f6f6f6',
        #                          hull_highlightbackground='#b3b3b3',
        #                          state='balloon',
        #                          relmouse='both',
        #                          yoffset=18,
        #                          xoffset=-2,
        #                          initwait=1300)

        self.mainframe = ttk.Frame(master)
        # self.topframe = ttk.Frame(self.mainframe, padding="5 8 5 5")
        self.topframe = ttk.Frame(self.mainframe, padding="6 2 6 2")

        self.centerframe = ttk.Frame(self.mainframe)

        self.leftframe = ttk.Frame(self.centerframe)
        self.leftframe.grid(column=0, row=1, sticky="nsew")

        self.centerframe.grid_columnconfigure(0, weight=1)
        self.centerframe.grid_columnconfigure(1, weight=0)
        self.centerframe.grid_rowconfigure(1, weight=1)

        self.bottomframe = ttk.Frame(self.mainframe)
        self.btnFont = tkinter.font.Font(family=ui_font(), size=10)
        self.statusFont = tkinter.font.Font(family=ui_font(), size=11)
        self.btnTxtColor = text_color()
        self.btnTxtColor_active = "white"

        self.tree = ttk.Treeview(self.leftframe, height=60, selectmode='browse')

        # get status bar
        self.my_statusbar = StatusBar(self.mainframe)

        self.configure_tree_style()

        self.style.configure('Treeview', relief='flat', borderwidth=0)

        self.style.configure('TButton', font=self.btnFont)
        if text_color():
            self.style.configure('TButton', foreground=text_color())

        self.compose_frames()

        self.vsb = AutoScrollbar(self.leftframe,
                                 orient="vertical",
                                 command=self.tree.yview)
        self.configure_tree()
        self.my_statusbar.apply_appearance(self._is_dark())

    @property
    def screen_size(self):
        w = self.master.winfo_screenwidth()
        h = self.master.winfo_screenheight()
        return w, h

    def _is_dark(self):
        if self.style.theme_use() != 'aqua':
            return False
        # Cache briefly: this is queried often (styling, the 1s appearance
        # tick, the drop hint), but the underlying check can spawn a process.
        now = time.monotonic()
        if now - getattr(self, '_dark_cache_t', 0.0) < 0.5:
            return self._dark_cache
        self._dark_cache = self._detect_dark()
        self._dark_cache_t = now
        return self._dark_cache

    def _detect_dark(self):
        """Detect macOS dark mode authoritatively.

        ``defaults read -g AppleInterfaceStyle`` returns 'Dark' in dark mode
        and fails (no such key) in light mode. This is reliable across Tk
        versions, unlike reading 'systemWindowBackgroundColor', which can
        resolve to a stale value and make the appearance watcher miss a
        light/dark switch. The colour read is kept only as a fallback.
        """
        if platform.system() == 'Darwin':
            try:
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True, text=True, timeout=1)
                if result.returncode == 0:
                    return result.stdout.strip() == 'Dark'
                return False
            except Exception:
                pass
        try:
            rgb = self.winfo_rgb('systemWindowBackgroundColor')
            return sum(rgb) / 3 < 32768
        except tk.TclError:
            return False

    def _fg_color(self):
        if self.style.theme_use() != 'aqua':
            return 'grey22'
        # On aqua, use the dynamic system label color so the text (Treeview
        # body AND headings) follows light/dark automatically, instead of a
        # hard-coded colour that the native heading element tends to ignore
        # and that does not refresh reliably on an appearance change.
        return 'systemTextColor'

    def configure_tree_style(self):
        self.style.configure('Treeview',
                             font=(ui_font(), 11),
                             foreground=self._fg_color(),
                             rowheight=20)

        self.style.configure('Treeview.Heading',
                             font=(ui_font(), 11),
                             foreground=self._fg_color())

    def refresh_appearance(self):
        self.configure_tree_style()
        self.alternate_colors(self.tree)
        self.my_statusbar.apply_appearance(self._is_dark())
        self._last_dark = self._is_dark()

    def start_appearance_watch(self):
        self._last_dark = self._is_dark()
        self._appearance_tick()

    def _appearance_tick(self):
        if self.style.theme_use() == 'aqua':
            now_dark = self._is_dark()
            if now_dark != self._last_dark:
                self._last_dark = now_dark
                self.refresh_appearance()
        self.after(1000, self._appearance_tick)

    def compose_frames(self):
        self.topframe.pack(side='top', fill='x')
        self.separator = ttk.Separator(self.mainframe, orient='horizontal')
        self.separator.pack(side='bottom', fill='x')
        self.centerframe.pack(side='top', expand=True, fill='both')
        self.bottomframe.pack(side='bottom', fill='x')
        self.mainframe.pack(side='top', expand=True, fill='both')

        self.style.configure("secondary.TButton", font=(ui_font(), 11))

    def sort_by(self, tree, col, descending):
        """
        sort tree contents when a column header is clicked
        """
        data = [(tree.set(child, col), child)
                for child in tree.get_children('')]

        data = change_numeric(data)
        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)

        tree.heading(col, command=lambda col=col: self.sort_by(tree, col, int(not descending)))
        self.alternate_colors(tree)

    def alternate_colors(self, tree, reverse=False, fundo1=None, fundo2=None):
        if fundo1 is None or fundo2 is None:
            if self._is_dark():
                fundo1, fundo2 = '#1e1e1e', '#2a2a2a'
            else:
                fundo1, fundo2 = '#ffffff', '#f4f4f6'

        texto = self._fg_color()

        if reverse:
            odd = False
        else:
            odd = True

        for i in tree.get_children():
            if odd:
                tree.item(i, tags=("even",))
                odd = False
            else:
                tree.item(i, tags=("odd",))
                odd = True

        tree.tag_configure('even', background=fundo1, foreground=texto)
        tree.tag_configure('odd', background=fundo2, foreground=texto)
        self.update_idletasks()

    def configure_tree(self):
        _col_keys = {
            'icon': '',
            'file': 'File',
            'original_size': 'Original Size',
            'new_size': 'New Size',
            'percent_saved': '% Saved',
        }
        for col in self.tree['columns']:
            key = _col_keys.get(col, col.title())
            heading_text = '' if not key else i18n._(key)
            self.tree.heading(
                col, text=heading_text,
                # Sort by column by clicking on header: not sorting here,
                # because we need a sorting method that works with 'humanized'
                # file sizes...
                # command=lambda c=col: self.sort_by(self.tree, c, 0)
            )

        self.style.configure("Treeview.Heading",
                             font=(ui_font(), 11),
                             )

        # scrollbar for treeview
        self.tree.grid(column=0, row=0, sticky="nsew", in_=self.leftframe)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(column=1, row=0, sticky="ns", in_=self.leftframe)

    @staticmethod
    def popup_message(window, msg: str):
        """Mostrar um painel de notificação com uma mensagem

        Recebe como parâmetros o widget da janela onde deverá ser apresentado o
        painel de notificação e uma string com o texto a mostrar.
        """
        window.update_idletasks()
        x, y = int(window.master.winfo_width() / 2), 76

        window.popupframe = tk.Frame(window.master, background="grey75")
        window.internalframe = tk.Frame(window.popupframe,
                                        background="white",
                                        padx=4, pady=4)

        window.msglabel = tk.Label(window.internalframe,
                                   font=tkinter.font.Font(family=ui_font(), size=11),
                                   foreground="grey22",
                                   text=msg)

        window.internalframe.pack(side="top", padx=1, pady=1)

        window.msglabel.pack()
        for i in range(1, 10, 2):
            window.popupframe.place(x=x, y=y + i, anchor="n", bordermode="outside")
            window.popupframe.update()
        window.popupframe.after(1500, window.popupframe.destroy)
