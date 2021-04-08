import tkinter as tk
from tkinter import ttk, messagebox
#import Pmw


from optimize_images_x.gui.extra_tk_utilities.auto_scrollbar import AutoScrollbar
from optimize_images_x.gui.extra_tk_utilities.label_entry import LabelEntry
from optimize_images_x.gui.extra_tk_utilities.label_text import LabelText


class SettingsWindow(ttk.Frame):
    """ Classe de base para a janela de detalhes de reparações """

    def __init__(self, master, num_contacto, estado_app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.estado_app = estado_app
        self.main_statusbar = estado_app.main_window.my_statusbar
        self.main_statusbar.show_progress(value=50, mode="determinate")
        self.master.bind("<Command-width>", self.on_btn_fechar)
        self.master.focus()

        self.main_statusbar.hide_progress(last_update=100)
        self.contacto_selecionado = ""
        self.rep_newDetailsWindow = {}
        self.rep_detail_windows_count = 0
        self.contacto_newDetailsWindow = {}
        self.contact_detail_windows_count = 0
        self.soma_reparacoes = 0
        self.soma_reincidencias = 0
        self.new_contact_telefone = ""
        self.new_contact_telemovel = ""
        self.new_contact_tel_emp = ""

        self.var_tipo_is_cliente = tk.IntVar()
        self.var_tipo_is_fornecedor = tk.IntVar()
        #self.var_tipo_is_loja = tk.IntVar()

        self.configurar_frames_e_estilos()
        self.montar_barra_de_ferramentas()

        self.gerar_painel_principal()

        if True:
        #if self.var_tipo_is_cliente.get():
            self.atualizar_soma()
            self.alternar_cores(self.tree)

        self.mostrar_painel_principal()
        self.montar_rodape()
        self.composeFrames()


    def montar_barra_de_ferramentas(self):
        self.lbl_titulo = ttk.Label(self.topframe, style="Panel_Title.TLabel",
                                    foreground=self.btnTxtColor, text=f"Contacto nº {self.num_contacto}")

        # ----------- Botão com menu "Copiar" --------------
        self.mbtn_copiar = ttk.Menubutton(self.topframe, text=" ⚡")
        self.mbtn_copiar.menu = tk.Menu(self.mbtn_copiar, tearoff=0)
        self.mbtn_copiar["menu"] = self.mbtn_copiar.menu
        self.mbtn_copiar.menu.add_command(label="Nome",
            command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_nome.get()))
        self.mbtn_copiar.menu.add_command(label="Número de contribuinte", command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_nif.get()))
        self.mbtn_copiar.menu.add_separator()
        self.mbtn_copiar.menu.add_command(label="Morada", command=lambda: self.copiar_para_clibpboard(self.ef_lstxt_morada.get()))
        self.mbtn_copiar.menu.add_command(label="Código Postal", command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_cod_postal.get()))
        self.mbtn_copiar.menu.add_command(label="Localidade", command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_localidade.get()))
        self.mbtn_copiar.menu.add_separator()
        self.mbtn_copiar.menu.add_command(label="Email", command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_email.get()))
        self.mbtn_copiar.menu.add_separator()
        self.mbtn_copiar.menu.add_command(label="Telefone", command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_telefone.get()))
        self.mbtn_copiar.menu.add_command(label="Telemóvel",
                                          command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_tlm.get()))
        self.mbtn_copiar.menu.add_command(label="Telefone na empresa",
                                          command=lambda: self.copiar_para_clibpboard(self.ef_ltxt_tel_empresa.get()))
        self.dicas.bind(
            self.mbtn_copiar, 'Clique para selecionar e copiar\ndados referentes a este contacto\npara a Área de Transferência.')
        # ----------- fim de Botão com menu "Copiar" -------------

        self.btn_nova_rep = ttk.Button(
            self.topframe, text="Criar reparação", style="secondary.TButton", command=self._on_criar_nova_reparacao)
        self.dicas.bind(self.btn_nova_rep, 'Criar um novo processo de reparação.')

        self.btn_guardar_alteracoes = ttk.Button(
            self.topframe, text="Guardar", style="secondary.TButton",
            command=self._on_update_contact)
        self.dicas.bind(self.btn_guardar_alteracoes,
                        'Clique para guardar quaisquer alterações\nefetuadas a esta ficha de contacto.')

        self.lbl_titulo.grid(column=0, row=0, rowspan=2)
        self.mbtn_copiar.grid(column=7, row=0)
        self.btn_nova_rep.grid(column=8, row=0)
        self.btn_guardar_alteracoes.grid(column=9, row=0)

        self.topframe.grid_columnconfigure(2, weight=1)

    def gerar_painel_principal(self):
        # Preparar o notebook da secção principal ------------------------
        self.note = ttk.Notebook(self.centerframe, padding="3 20 3 3")
        self.note.bind_all("<<NotebookTabChanged>>", self._on_tab_changed)

        self.tab_geral = ttk.Frame(self.note, padding=10)
        self.tab_notas = ttk.Frame(self.note, padding=10)
        self.note.add(self.tab_geral, text="Contactos")
        self.note.add(self.tab_notas, text="Informação Adicional")
        self.gerar_tab_geral()
        self.montar_tab_geral()
        self.gerar_tab_notas()
        self.montar_tab_notas()

        if True:
        #if self.var_tipo_is_cliente.get():
            self.tab_reparacoes = ttk.Frame(self.note, padding=0)
            self.note.add(self.tab_reparacoes, text="Reparações")
            self.gerar_tab_reparacoes()
            self.montar_tab_reparacoes()


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

        #self.geral_fr2 = ttk.Frame(self.tab_geral)

        # Criar widgets para este separador -----------------------------------
        #self.txt_numero_contacto = ttk.Entry(self.geral_fr1, font=("Helvetica-Neue", 12), width=5)
        #self.txt_nome = ttk.Entry(self.geral_fr1, font=("Helvetica-Neue", 12), width=35)




    def montar_tab_geral(self):
        # Montar todos os campos na grid --------------------------------------
        self.ef_ltxt_nome.grid(
            column=0, row=0, columnspan=3, padx=5, sticky='we')
        self.ef_ltxt_empresa.grid(
            column=0, row=1, columnspan=2, padx=5, sticky='we')
        self.ef_ltxt_nif.grid(column=2, row=1, padx=5, sticky='we')

        self.ef_ltxt_telefone.grid(column=0, row=2, padx=5, sticky='we')
        self.ef_ltxt_tlm.grid(column=1, row=2, padx=5, sticky='we')
        self.ef_ltxt_tel_empresa.grid(column=2, row=2, padx=5, sticky='we')
        self.ef_ltxt_email.grid(
            column=0, row=3, columnspan=3, padx=5, sticky='we')

        self.geral_fr1.grid_columnconfigure(0, weight=1)
        self.geral_fr1.grid_columnconfigure(1, weight=1)
        self.geral_fr1.grid_columnconfigure(2, weight=1)

        self.geral_fr1.pack(side='top', expand=False, fill='x')
        #ttk.Separator(self.tab_geral).pack(side='top', expand=False, fill='x', pady=10)
        #self.geral_fr2.pack(side='top', expand=True, fill='both')

        self.ef_lstxt_morada.grid(
            column=0, row=4, columnspan=3, rowspan=2, padx=5, sticky='we')

        self.ef_ltxt_cod_postal.grid(column=0, row=6, padx=5, sticky='we')
        self.ef_ltxt_localidade.grid(
            column=1, row=6, columnspan=2, padx=5, sticky='we')

        self.ef_lbl_pais.grid(column=0, columnspan=3,
                              row=7, padx=5, sticky='we')
        self.ef_combo_pais.grid(column=0, columnspan=3,
                                row=8, padx=5, sticky='we')

        self.morada_fr1.grid_columnconfigure(0, weight=1)
        self.morada_fr1.grid_columnconfigure(1, weight=1)
        self.morada_fr1.grid_columnconfigure(2, weight=1)

        self.morada_fr1.pack(side='top', expand=False, fill='x')

    def gerar_tab_notas(self):
        self.notas_fr1 = ttk.Frame(self.tab_notas)
        #self.notas_fr2 = ttk.Frame(self.tab_notas)
        self.ef_cabecalho = ttk.Frame(self.notas_fr1, padding=4)
        self.ef_lbl_tipo = ttk.Label(
            self.ef_cabecalho, text="Tipo:", style="Panel_Body.TLabel")
        self.ef_chkbtn_tipo_cliente = ttk.Checkbutton(
            self.ef_cabecalho, text="Cliente", variable=self.var_tipo_is_cliente)
        self.ef_chkbtn_tipo_fornecedor = ttk.Checkbutton(
            self.ef_cabecalho, text="Fornecedor ou centro técnico", variable=self.var_tipo_is_fornecedor)
        #self.ef_chkbtn_tipo_loja = ttk.Checkbutton(self.ef_cabecalho, text="Loja do nosso grupo", style="Panel_Body.Checkbutton", variable=self.var_tipo_is_loja)

        self.ef_lstxt_notas = LabelText(
            self.notas_fr1, "\nNotas:", height=3, style="Panel_Body.TLabel")


        self.var_tipo_is_cliente.set(self.contacto['is_cliente'])
        self.var_tipo_is_fornecedor.set(self.contacto['is_fornecedor'])
        # self.var_tipo_is_loja.set(False)
        self.ef_lstxt_notas.set(self.contacto['notas'])


    def montar_tab_notas(self):
        self.ef_lstxt_notas.grid(
            column=0, row=9, columnspan=3, rowspan=4, padx=5, sticky='wens')
        self.ef_cabecalho.columnconfigure(2, weight=1)
        #self.notas_fr1.columnconfigure(0, weight=1)

        self.ef_lbl_tipo.grid(column=0, row=1, sticky='e')
        self.ef_chkbtn_tipo_cliente.grid(column=1, row=1, sticky='width')
        self.ef_chkbtn_tipo_fornecedor.grid(column=1, row=2, sticky='width')
        #self.ef_chkbtn_tipo_loja.grid(column=1, row=3, sticky='width')

        self.ef_cabecalho.grid(column=0, row=0, sticky='we')

        self.notas_fr1.columnconfigure(0, weight=1)
        self.notas_fr1.rowconfigure(10, weight=1)

        self.notas_fr1.pack(side='top', expand=True, fill='both')
        #ttk.Separator(self.tab_notas).pack(side='top', expand=False, fill='x', pady=10)
        #self.notas_fr2.pack(side='top', expand=True, fill='both')

    def gerar_tab_reparacoes(self):  # TODO
        self.reparacoes_fr1 = ttk.Frame(self.tab_reparacoes)
        self.treeframe = ttk.Frame(self.reparacoes_fr1, padding="0 0 0 0")

    def montar_tab_reparacoes(self):
        self.reparacoes_fr1.pack(side='top', expand=True, fill='both')
        self.treeframe.grid(column=0, row=0, sticky="nsew")
        self.treeframe.grid_columnconfigure(0, weight=1)
        self.treeframe.grid_rowconfigure(0, weight=1)

        self.lbl_soma_processos.grid(
            column=0, row=2, sticky='ne', pady="5 10", padx=3)

        self.reparacoes_fr1.grid_columnconfigure(0, weight=1)
        self.reparacoes_fr1.grid_rowconfigure(0, weight=1)
        self.atualizar_soma()


    def on_btn_fechar(self, event):
        """ will test for some condition before closing, save if necessary and
                then call destroy()
        """
        window = event.widget.winfo_toplevel()
        window.destroy()


    def mostrar_painel_principal(self):
        self.note.pack(side='top', expand=True, fill='both')
        self.note.enable_traversal()

    def montar_rodape(self):
        nome_cr = self.contacto['criado_por_utilizador_nome']
        data_cr = self.contacto['created_on']
        txt_esquerda = f"Criado por {nome_cr} em {data_cr}."

        if self.contacto['atualizado_por_utilizador_nome'] is None:
            txt_direita = ""
        else:
            nome_updt = self.contacto['atualizado_por_utilizador_nome']
            data_updt = self.contacto['updated_on']
            txt_direita = f"Atualizado por {nome_updt} em {data_updt}."

        self.rodapeFont = tk.font.Font(family="Lucida Grande", size=9)
        self.rodapeTxtColor = "grey22"

        self.esquerda = ttk.Label(self.bottomframe, anchor='width', text=txt_esquerda,
                                  font=self.rodapeFont, foreground=self.rodapeTxtColor)
        self.direita = ttk.Label(self.bottomframe, anchor='e', text=txt_direita,
                                 font=self.rodapeFont, foreground=self.rodapeTxtColor)
        self.esquerda.pack(side="left")
        self.direita.pack(side="right")


    def atualizar_rodape(self):
        try:
            #self.contacto = db.obter_contacto(self.num_contacto)
            nome_updt = self.contacto['atualizado_por_utilizador_nome']
            data_updt = self.contacto['updated_on']
            txt_direita = f"Atualizado por {nome_updt} em {data_updt}."
            self.direita.config(text=txt_direita)
        except:
            pass

    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.selectItem_popup)
        self.tree.bind('<Double-1>', lambda x: self.create_window_detalhe_rep(
            num_reparacao=self.reparacao_selecionada))
        self.tree.bind("<Button-2>", self.popupMenu)
        self.tree.bind("<Button-3>", self.popupMenu)
        self.update_idletasks()

    def unbind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', None)
        self.tree.bind('<Double-1>', None)
        self.tree.bind("<Button-2>", None)
        self.tree.bind("<Button-3>", None)
        self.update_idletasks()

    def create_window_detalhe_rep(self, num_reparacao=None):
        self.rep_detail_windows_count += 1
        self.rep_newDetailsWindow[self.rep_detail_windows_count] = tk.Toplevel()
        # self.janela_detalhes_rep = detalhe_reparacao.repairDetailWindow(
        #     self.rep_newDetailsWindow[self.rep_detail_windows_count],
        #     num_reparacao, self.estado_app)

    def configurar_frames_e_estilos(self):
        # self.master.minsize(W_DETALHE_CONTACTO_MIN_WIDTH, W_DETALHE_CONTACTO_MIN_HEIGHT)
        # self.master.maxsize(W_DETALHE_CONTACTO_MAX_WIDTH, W_DETALHE_CONTACTO_MAX_HEIGHT)
        # self.master.geometry(W_DETALHE_CONTACTO_GEOMETRIA)  # Se ativada esta
        # linha, deixa de atualizar as medidas da janela ao mudar de separador
        self.master.title(f"Contacto nº{self.num_contacto}")

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
        self.bottomframe = ttk.Frame(self.mainframe, padding="3 1 3 1")

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
        self.bottomframe.pack(side=tk.BOTTOM, fill=tk.X)
        self.mainframe.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
