import tkinter as tk
import tkinter.font
from tkinter import ttk


# import Pmw


class SettingsWindow(ttk.Frame):
    """ Classe de base para a janela de detalhes de reparações """

    def __init__(self, master, app_status, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.app_status = app_status
        self.master.bind("<Command-w>", self.on_btn_close)
        self.master.focus()

        self.configurar_frames_e_estilos()
        self.gerar_painel_principal()
        self.mostrar_painel_principal()
        self.composeFrames()

    def gerar_painel_principal(self):
        self.note = ttk.Notebook(self.centerframe, padding="3 20 3 3")
        self.note.bind_all("<<NotebookTabChanged>>", self._on_tab_changed)

        self.tab_geral = ttk.Frame(self.note, padding=10)
        self.tab_jpeg = ttk.Frame(self.note, padding=10)
        self.tab_png = ttk.Frame(self.note, padding=10)
        self.note.add(self.tab_geral, text="General")
        self.note.add(self.tab_jpeg, text="JPEG")
        self.note.add(self.tab_png, text="PNG")
        self.gerar_tab_geral()
        self.montar_tab_geral()
        self.gerar_tab_jpeg()
        self.montar_tab_png()

    def _on_tab_changed(self, event):
        w = event.widget  # get the current widget
        w.update_idletasks()
        # get the tab widget where we're going to
        tab = w.nametowidget(w.select())
        # get the tab widget where we're going to
        tab_name = self.note.tab(self.note.select(), "text")
        # if tab_name == "Reparações":
        #     w.update_idletasks()
        #     self.master.state("zoomed")
        #     self.master.minsize(820, W_DETALHE_CONTACTO_MIN_HEIGHT)
        # elif tab_name == "Informação Adicional":
        #     self.master.minsize(W_DETALHE_CONTACTO_MIN_WIDTH, 360)
        #     w.update_idletasks()
        #     self.master.state("normal")
        #     w.configure(height=tab.winfo_reqheight(),
        #                 width=tab.winfo_reqwidth())
        # else:
        #     self.master.minsize(W_DETALHE_CONTACTO_MIN_WIDTH,
        #                         W_DETALHE_CONTACTO_MIN_HEIGHT)
        #     w.update_idletasks()
        #     self.master.state("normal")
        #     w.configure(height=tab.winfo_reqheight(),
        #                 width=tab.winfo_reqwidth())

    def gerar_tab_geral(self):
        # TAB Geral ~~~~~~~~~~~~~~~~
        self.geral_fr1 = ttk.Frame(self.tab_geral)
        self.morada_fr1 = ttk.Frame(self.tab_geral)

        # self.geral_fr2 = ttk.Frame(self.tab_geral)

        # Criar widgets para este separador -----------------------------------
        # self.txt_numero_contacto = ttk.Entry(self.geral_fr1, font=("Helvetica-Neue", 12), width=5)
        # self.txt_nome = ttk.Entry(self.geral_fr1, font=("Helvetica-Neue", 12), width=35)

    # def montar_tab_geral(self):
    #     # Montar todos os campos na grid --------------------------------------
    #     self.ef_ltxt_nome.grid(
    #         column=0, row=0, columnspan=3, padx=5, sticky='we')
    #     self.ef_ltxt_empresa.grid(
    #         column=0, row=1, columnspan=2, padx=5, sticky='we')
    #     self.ef_ltxt_nif.grid(column=2, row=1, padx=5, sticky='we')
    #
    #     self.ef_ltxt_telefone.grid(column=0, row=2, padx=5, sticky='we')
    #     self.ef_ltxt_tlm.grid(column=1, row=2, padx=5, sticky='we')
    #     self.ef_ltxt_tel_empresa.grid(column=2, row=2, padx=5, sticky='we')
    #     self.ef_ltxt_email.grid(
    #         column=0, row=3, columnspan=3, padx=5, sticky='we')
    #
    #     self.geral_fr1.grid_columnconfigure(0, weight=1)
    #     self.geral_fr1.grid_columnconfigure(1, weight=1)
    #     self.geral_fr1.grid_columnconfigure(2, weight=1)
    #
    #     self.geral_fr1.pack(side='top', expand=False, fill='x')
    #     # ttk.Separator(self.tab_geral).pack(side='top', expand=False, fill='x', pady=10)
    #     # self.geral_fr2.pack(side='top', expand=True, fill='both')
    #
    #     self.ef_lstxt_morada.grid(
    #         column=0, row=4, columnspan=3, rowspan=2, padx=5, sticky='we')
    #
    #     self.ef_ltxt_cod_postal.grid(column=0, row=6, padx=5, sticky='we')
    #     self.ef_ltxt_localidade.grid(
    #         column=1, row=6, columnspan=2, padx=5, sticky='we')
    #
    #     self.ef_lbl_pais.grid(column=0, columnspan=3,
    #                           row=7, padx=5, sticky='we')
    #     self.ef_combo_pais.grid(column=0, columnspan=3,
    #                             row=8, padx=5, sticky='we')
    #
    #     self.morada_fr1.grid_columnconfigure(0, weight=1)
    #     self.morada_fr1.grid_columnconfigure(1, weight=1)
    #     self.morada_fr1.grid_columnconfigure(2, weight=1)
    #
    #     self.morada_fr1.pack(side='top', expand=False, fill='x')

    def gerar_tab_jpeg(self):
        self.notas_fr1 = ttk.Frame(self.tab_jpeg)
        # self.notas_fr2 = ttk.Frame(self.tab_jpeg)
        # self.ef_cabecalho = ttk.Frame(self.notas_fr1, padding=4)
        # self.ef_lbl_tipo = ttk.Label(
        #     self.ef_cabecalho, text="Tipo:", style="Panel_Body.TLabel")
        # self.ef_chkbtn_tipo_cliente = ttk.Checkbutton(
        #     self.ef_cabecalho, text="Cliente", variable=self.var_tipo_is_cliente)
        # self.ef_chkbtn_tipo_fornecedor = ttk.Checkbutton(
        #     self.ef_cabecalho, text="Fornecedor ou centro técnico", variable=self.var_tipo_is_fornecedor)
        # # self.ef_chkbtn_tipo_loja = ttk.Checkbutton(self.ef_cabecalho, text="Loja do nosso grupo", style="Panel_Body.Checkbutton", variable=self.var_tipo_is_loja)
        #
        # self.ef_lstxt_notas = LabelText(
        #     self.notas_fr1, "\nNotas:", height=3, style="Panel_Body.TLabel")
        #
        # self.var_tipo_is_cliente.set(self.contacto['is_cliente'])
        # self.var_tipo_is_fornecedor.set(self.contacto['is_fornecedor'])
        # # self.var_tipo_is_loja.set(False)
        # self.ef_lstxt_notas.set(self.contacto['notas'])

    def montar_tab_png(self):
        pass


    def on_btn_close(self, event):
        """ will test for some condition before closing, save if necessary and
                then call destroy()
        """
        window = event.widget.winfo_toplevel()
        window.destroy()

    def mostrar_painel_principal(self):
        self.note.pack(side='top', expand=True, fill='both')
        self.note.enable_traversal()


    def configurar_frames_e_estilos(self):
        self.master.minsize(640, 360)
        # self.master.maxsize(W_DETALHE_CONTACTO_MAX_WIDTH, W_DETALHE_CONTACTO_MAX_HEIGHT)

        self.master.title("Preferences")

        # self.dicas = Pmw.Balloon(self.master, label_background='#f6f6f6',
        #                          hull_highlightbackground='#b3b3b3',
        #                          state='balloon',
        #                          relmouse='both',
        #                          yoffset=18,
        #                          xoffset=-2,
        #                          initwait=1300)

        self.mainframe = ttk.Frame(self.master)
        self.topframe = ttk.Frame(self.mainframe, padding="5 8 5 5")
        self.centerframe = ttk.Frame(self.mainframe)

        self.estilo = ttk.Style()
        self.estilo.configure("Panel_Title.TLabel", pady=10, foreground="grey25", font=(
            "Helvetica Neue", 18, "bold"))
        self.estilo.configure("Panel_Body.TLabel", font=("Lucida Grande", 11))
        self.estilo.configure("TMenubutton", font=("Lucida Grande", 11))
        self.estilo.configure('Reparacoes_Remessa.Treeview', rowheight=42)

        self.btnFont = tk.font.Font(family="Lucida Grande", size=10)
        self.btnTxtColor = "grey22"

    def composeFrames(self):
        self.topframe.pack(side=tk.TOP, fill=tk.X)
        self.centerframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.mainframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def montar_tab_geral(self):
        pass
