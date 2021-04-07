import tkinter as tk
import tkinter.font
from tkinter import ttk

from optimize_images_x.gui.extra_tk_utilities.auto_scrollbar import AutoScrollbar
from optimize_images_x.gui.extra_tk_utilities.status_bar import StatusBar


# import Pmw


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
        self.estilo = ttk.Style()

        # self.dicas = Pmw.Balloon(self.master, label_background='#f6f6f6',
        #                          hull_highlightbackground='#b3b3b3',
        #                          state='balloon',
        #                          relmouse='both',
        #                          yoffset=18,
        #                          xoffset=-2,
        #                          initwait=1300)

        self.mainframe = ttk.Frame(master)
        self.topframe = ttk.Frame(self.mainframe, padding="5 8 5 5")
        self.centerframe = ttk.Frame(self.mainframe)

        self.leftframe = ttk.Frame(self.centerframe)
        self.leftframe.grid(column=0, row=1, sticky="nsew")

        self.centerframe.grid_columnconfigure(0, weight=1)
        self.centerframe.grid_columnconfigure(1, weight=0)
        self.centerframe.grid_rowconfigure(1, weight=1)

        self.bottomframe = ttk.Frame(self.mainframe)
        self.btnFont = tkinter.font.Font(family="Lucida Grande", size=10)
        self.statusFont = tkinter.font.Font(family="Lucida Grande", size=11)
        self.btnTxtColor = "grey22"
        self.btnTxtColor_active = "white"

        self.tree = ttk.Treeview(
            self.leftframe, height=60, selectmode='browse')

        # get status bar
        self.my_statusbar = StatusBar(self.mainframe)

        self.estilo.configure('Treeview', font=(
            "Lucida Grande", 11), foreground="grey22", rowheight=20)
        self.estilo.configure('Treeview.Heading', font=(
            "Lucida Grande", 11), foreground="grey22")
        self.estilo.configure('Treeview', relief='flat', borderwidth=0)

        self.compose_frames()

        self.vsb = AutoScrollbar(self.leftframe,
                                 orient="vertical",
                                 command=self.tree.yview)
        self.configurar_tree()

    @property
    def screen_size(self):
        w = self.master.winfo_screenwidth()
        h = self.master.winfo_screenheight()
        return w, h

    def compose_frames(self):
        self.topframe.pack(side='top', fill='x')
        self.centerframe.pack(side='top', expand=True, fill='both')
        self.bottomframe.pack(side='bottom', fill='x')
        self.mainframe.pack(side='top', expand=True, fill='both')

        self.estilo.configure("secondary.TButton", font=("Lucida Grande", 11))

    # ------ Permitir que a tabela possa ser ordenada clicando no cabeçalho --
    @staticmethod
    def is_numeric(s):
        """
        test if a string s is numeric
        """
        numeric: bool = False
        for c in s:
            if c in "1234567890.":
                numeric = True
            else:
                return False
        return numeric

    def change_numeric(self, data):
        """
        if the data to be sorted is numeric change to float
        """
        new_data = []
        if self.is_numeric(data[0][0]):
            # change child to a float
            for child, col in data:
                new_data.append((float(child), col))
            return new_data
        return data

    def sort_by(self, tree, col, descending):
        """
        sort tree contents when a column header is clicked
        """
        data = [(tree.set(child, col), child)
                for child in tree.get_children('')]

        data = self.change_numeric(data)
        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)

        tree.heading(col, command=lambda col=col: self.sort_by(tree, col, int(not descending)))

        self.alternar_cores(tree)

    # ------ Fim das funções relacionadas c/ o ordenamento da tabela ---------

    def alternar_cores(self, tree, inverso=False, fundo1='grey98', fundo2='white'):
        if inverso:
            impar = False
        else:
            impar = True

        for i in tree.get_children():
            if impar:
                tree.item(i, tags=("par",))
                impar = False
            else:
                tree.item(i, tags=("impar",))
                impar = True

        tree.tag_configure('par', background=fundo1)
        tree.tag_configure('impar', background=fundo2)
        self.update_idletasks()

    def configurar_tree(self):
        # Ordenar por coluna ao clicar no respetivo cabeçalho
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: self.sort_by(self.tree, c, 0))

        # Barra de deslocação para a tabela
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
                                   font=tkinter.font.Font(family="Lucida Grande", size=11),
                                   foreground="grey22",
                                   text=msg)

        window.internalframe.pack(side="top", padx=1, pady=1)

        window.msglabel.pack()
        for i in range(1, 10, 2):
            window.popupframe.place(x=x, y=y + i, anchor="n", bordermode="outside")
            window.popupframe.update()
        window.popupframe.after(1500, window.popupframe.destroy)
