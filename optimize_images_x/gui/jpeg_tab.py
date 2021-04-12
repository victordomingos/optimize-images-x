import tkinter as tk
from tkinter import ttk, messagebox

from printing import imprimir
from gui.base_app import baseApp
from gui.extra_tk_utilities import AutoScrollbar
from gui.detalhe_remessa import remessaDetailWindow
from global_setup import *
from misc.constants import *


if USE_LOCAL_DATABASE:
    from local_db import db_main as db
else:
    from remote_db import db_main as db


class RemessasWindow(baseApp):
    """ Classe de base para a janela de remessas """

    def __init__(self, master, estado_app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.estado_app = estado_app
        self.master = master

        # Obtém uma referência para a barra de estado da janela principal,
        # para poder utilizar a barra de progresso nessa janela.
        self.main_statusbar = estado_app.main_window.my_statusbar
        self.main_statusbar.show_progress(value=50, mode="determinate")
        self.master.minsize(REMESSAS_MIN_WIDTH, REMESSAS_MIN_HEIGHT)
        self.master.maxsize(REMESSAS_MAX_WIDTH, REMESSAS_MAX_HEIGHT)

        width, height = self.screen_size()
        main_width = self.estado_app.main_window.master.winfo_width()

        if width - REMESSAS_MIN_WIDTH < main_width:
            pos_x = width - REMESSAS_MIN_WIDTH
        else:
            pos_x = main_width + 1

        if height < (REMESSAS_MIN_HEIGHT + 92):
            pos_y = height - REMESSAS_MIN_HEIGHT - 22
        else:
            pos_y = 92

        self.master.geometry(f'{REMESSAS_MIN_WIDTH}x{REMESSAS_MIN_HEIGHT}+{pos_x}+{pos_y}')

        self.master.title('Remessas')
        self.remessa_selecionada = None
        self.remessa_newDetailsWindow = {}
        self.remessa_detail_windows_count = 0
        self.nremessas = 0

        self.montar_barra_de_ferramentas()
        self.montar_tabela()

        self.gerar_painel_entrada()
        self.gerar_menu()

        self.composeFrames()
        self.main_statusbar.hide_progress(last_update=100)
        self.my_statusbar.show_progress(value=30, length=60, mode="determinate")
        self.inserir_dados_de_exemplo()  # TODO: obter dados da base de dados
        self.my_statusbar.progress_update(70)

        self.alternar_cores(self.tree)
        self.atualizar_soma()
        if self.estado_app.painel_nova_remessa_aberto:
            self.mostrar_painel_entrada()
        self.my_statusbar.hide_progress(last_update=100)


    def gerar_menu(self):
        self.menu = tk.Menu(self.master)
        #----------------Menu contextual tabela principal---------------------
        self.contextMenu = tk.Menu(self.menu)
        self.contextMenu.add_command(label="Informações", command=lambda: self.create_window_detalhe_remessa(
            num_remessa=self.remessa_selecionada))
        #self.contextMenu.add_command(label="Abrir no site da transportadora", command=self.abrir_url_browser)
        self.contextMenu.add_separator()
        #self.contextMenu.add_command(label="Copiar número de objeto", command=self.copiar_obj_num)
        #self.contextMenu.add_command(label="Copiar mensagem de expedição", command=self.copiar_msg)
        # self.contextMenu.add_separator()
        #self.contextMenu.add_command(label="Arquivar/restaurar remessa", command=self.del_remessa)
        # self.contextMenu.add_separator()
        #self.contextMenu.add_command(label="Registar cheque recebido", command=self.pag_recebido)
        #self.contextMenu.add_command(label="Registar cheque depositado", command=self.chq_depositado)

    def contar_linhas(self):
        """ Obtém o número de linhas da tabela de remessas. """
        linhas = self.tree.get_children("")
        return len(linhas)

    def atualizar_soma(self):
        """
        Atualiza a barra de estado com o número de remessas.
        """
        self.nremessas = self.contar_linhas()
        self.my_statusbar.set(f"{self.nremessas} remessas")

    def montar_tabela(self):
        self.tree = ttk.Treeview(
            self.leftframe, height=60, selectmode='browse')
        self.tree['columns'] = ('ID', 'Origem', 'Destino', 'Qtd.', 'Data')
        self.tree.pack(side=tk.TOP, fill=tk.BOTH)
        self.tree.column('#0', anchor=tk.W, minwidth=0, stretch=0, width=0)
        self.tree.column('ID', anchor=tk.E, minwidth=37, stretch=0, width=37)
        self.tree.column('Origem', minwidth=60, stretch=1, width=60)
        self.tree.column('Destino', minwidth=60, stretch=1, width=60)
        self.tree.column('Qtd.', anchor=tk.E, minwidth=40, stretch=0, width=40)
        self.tree.column('Data', anchor=tk.E, minwidth=90, stretch=0, width=90)

        self.configurarTree()
        self.leftframe.grid_columnconfigure(0, weight=1)
        self.leftframe.grid_rowconfigure(0, weight=1)
        self.bind_tree()

    def montar_barra_de_ferramentas(self):
        # Barra de ferramentas / botões ---------------------------------------

        self.btn_entrada = ttk.Button(
            self.topframe, style="secondary.TButton", text="Entrada", command=None)
        self.btn_entrada.grid(column=0, row=0)
        self.dicas.bind(
            self.btn_entrada, 'Mostrar apenas remessas de entrada \n(receção de artigos enviados por\nfornecedores e/ou centros técnicos).')

        self.btn_saida = ttk.Button(
            self.topframe, style="secondary.TButton", text="Saída", command=None)
        self.btn_saida.grid(column=1, row=0)
        self.dicas.bind(
            self.btn_saida, 'Mostrar apenas remessas de saída \n(envio de artigos para fornecedores \ne/ou centros técnicos).')

        self.btn_add = ttk.Button(
            self.topframe, text=" ➕", width=3, command=self.show_entryform)
        self.btn_add.grid(column=3, row=0)
        self.dicas.bind(self.btn_add, 'Criar nova remessa. (⌘N)')

        self.text_input_pesquisa = ttk.Entry(self.topframe, width=12)
        self.text_input_pesquisa.grid(column=4, row=0)
        self.dicas.bind(self.text_input_pesquisa,
                        'Para iniciar a pesquisa, digite\numa palavra ou frase. (⌘F)')

        #letras_etc = ascii_letters + "01234567890-., "
        # for char in letras_etc:
        #    keystr = '<KeyRelease-' + char + '>'
        #    self.text_input_pesquisa.bind(keystr, self.ativar_pesquisa)
        #self.text_input_pesquisa.bind('<Button-1>', self.clique_a_pesquisar)
        #self.text_input_pesquisa.bind('<KeyRelease-Escape>', self.cancelar_pesquisa)
        #self.text_input_pesquisa.bind('<KeyRelease-Mod2-a>', self.text_input_pesquisa.select_range(0, END))

        for col in range(1, 4):
            self.topframe.columnconfigure(col, weight=0)
        self.topframe.columnconfigure(2, weight=1)

    def mostrar_painel_entrada(self, *event):
        self.estado_app.painel_nova_remessa_aberto = True
        self.show_entryform()
        self.liga_desliga_menu_novo()
        self.my_statusbar.set(self.str_num_processos)
        self.ef_radio_tipo_saida.focus()

    def fechar_painel_entrada(self, *event):
        self.estado_app.painel_nova_remessa_aberto = False
        self.clear_text()
        self.hide_entryform()
        self.liga_desliga_menu_novo()
        self.update()
        self.estado_app.main_window.bind_all("<Command-r>", lambda
            *x: self.estado_app.main_window.create_window_remessas(criar_nova_remessa=True))

    def gerar_painel_entrada(self):
        # entryfr1-----------------------------
        self.ef_var_tipo = tk.IntVar()
        self.ef_var_tipo.set(0)
        self.ef_var_destino = tk.IntVar()
        self.num_processos = 0
        self.str_num_processos = f"Número de processos a enviar: {self.num_processos}"
        self.ef_var_reparacoes_a_enviar = tk.IntVar()
        self.ef_var_reparacoes_a_enviar.set("Selecionar reparações...")

        self.ef_var_destino.set("Selecionar centro técnico...")

        self.ef_cabecalho = ttk.Frame(self.entryfr1, padding=4)
        self.ef_lbl_titulo = ttk.Label(
            self.ef_cabecalho, style="Panel_Title.TLabel", text="Adicionar Remessa:")
        self.ef_lbl_tipo = ttk.Label(
            self.ef_cabecalho, text="Tipo:", style="Panel_Body.TLabel")
        self.ef_radio_tipo_saida = ttk.Radiobutton(self.ef_cabecalho, text="Envio", style="Panel_Body.TRadiobutton",
                                                   variable=self.ef_var_tipo, value=TIPO_REMESSA_ENVIO, command=self.radio_tipo_command)
        self.ef_radio_tipo_entrada = ttk.Radiobutton(self.ef_cabecalho, text="Receção", style="Panel_Body.TRadiobutton",
                                                     variable=self.ef_var_tipo, value=TIPO_REMESSA_RECECAO, command=self.radio_tipo_command)
        self.btn_adicionar = ttk.Button(self.ef_cabecalho, default="active",
                                        style="Active.TButton", text="Adicionar", command=self.on_save_remessa)
        self.btn_cancelar = ttk.Button(
            self.ef_cabecalho, text="Cancelar", command=self.on_remessa_cancel)

        self.ef_lbl_titulo.grid(column=0, row=0, columnspan=3, sticky="width", pady="0 10")
        self.ef_lbl_tipo.grid(column=0, row=1, sticky="e")
        self.ef_radio_tipo_saida.grid(column=1, row=1, sticky="width")
        self.ef_radio_tipo_entrada.grid(column=2, row=1, sticky="width")
        self.btn_adicionar.grid(column=3, row=1, sticky="we")
        self.btn_cancelar.grid(column=3, row=2, sticky="we")

        self.ef_cabecalho.grid(column=0, row=0, sticky='we')
        self.entryfr1.columnconfigure(0, weight=1)
        self.ef_cabecalho.columnconfigure(0, weight=0)
        self.ef_cabecalho.columnconfigure(2, weight=1)

        # self.btn_adicionar.bind('<Button-1>', self.add_remessa)

        # entryfr2-----------------------------
        self.ef_lbl_destino = ttk.Label(
            self.entryfr2, width=27, text="Destino:", style="Panel_Body.TLabel")
        self.ef_combo_destino = ttk.Combobox(self.entryfr2,
                                             width=40,
                                             textvariable=self.ef_var_destino,
                                             postcommand=self.atualizar_combo_lista_destino,
                                             state='readonly')  # TODO: Obter estes valores a partir da base de dados, a utilizar também no formulário de Remessas.
        self.ef_lbl_destino.grid(column=0, row=0, padx=5, sticky='we')
        self.ef_combo_destino.grid(column=0, row=1, padx=5, sticky='we', pady="0 5")
        self.dicas.bind(self.ef_combo_destino,
                        'Clique aqui para selecionar a partir\nde uma lista o fornecedor ou centro técnico.')
        self.entryfr2.grid_columnconfigure(0, weight=1)

        # Entryfr3
        self.ef_lbl_num_rep = ttk.Label(
            self.entryfr3, text="Nº rep.:", style="Panel_Body.TLabel")
        self.ef_txt_num_reparacao = ttk.Entry(self.entryfr3, width=7)
        self.dicas.bind(self.ef_txt_num_reparacao,
                        'Clique aqui para escrever o número de um\nprocesso de reparação a incluir na remessa.')

        self.ef_btn_adicionar_rep = ttk.Button(self.entryfr3, text="Inserir")
        self.dicas.bind(self.ef_btn_adicionar_rep,
                        'Clique aqui para incluir na remessa\no processo de reparação selecionado.')

        # TODO:Ir buscar à base de dados os processos a aguardar envio/receção?
        # Atualizar lista quando um dos processos é selecionado e quando é
        # alterado o tipo de remessa.
        self.ef_combo_selecionar_rep = ttk.Combobox(self.entryfr3,
                                                    textvariable=self.ef_var_reparacoes_a_enviar,
                                                    postcommand=self.atualizar_combo_lista_reparacoes,
                                                    state='readonly')
        self.dicas.bind(self.ef_combo_selecionar_rep,
                        'Clique aqui para selecionar a partir de\numa lista um processo de reparação\na incluir na remessa.')

        self.ef_lbl_num_rep.grid(column=0, row=0, padx=5, sticky='we')
        self.ef_txt_num_reparacao.grid(column=0, row=1, padx=5, sticky='we')
        self.ef_btn_adicionar_rep.grid(column=1, row=1, padx=5, sticky='width')
        self.ef_combo_selecionar_rep.grid(
            column=2, row=1, padx=5, sticky='we')
        self.entryfr3.grid_columnconfigure(0, weight=0)
        self.entryfr3.grid_columnconfigure(1, weight=0)
        self.entryfr3.grid_columnconfigure(2, weight=1)

        #  treeview entryfr4:
        self.ef_lista = ttk.Frame(self.entryfr4, padding=4)
        self.tree_lista_processos_remessa = ttk.Treeview(
            self.ef_lista, height=15, selectmode='browse')
        self.tree_lista_processos_remessa['columns'] = (
            'Nº', 'Equipamento', 'S/N')
        self.tree_lista_processos_remessa.pack(
            side=tk.TOP, expand=True, fill='both')
        self.tree_lista_processos_remessa.column(
            '#0', anchor=tk.W, minwidth=0, stretch=0, width=0)
        self.tree_lista_processos_remessa.column(
            'Nº', anchor=tk.E, minwidth=46, stretch=0, width=46)
        self.tree_lista_processos_remessa.column(
            'Equipamento', minwidth=180, stretch=1, width=180)
        self.tree_lista_processos_remessa.column(
            'S/N', anchor=tk.E, minwidth=140, stretch=0, width=140)
        self.configurarTree_lista_processos_remessa()
        self.ef_lista.grid(column=0, row=0, sticky='we')
        self.ef_lista.grid_columnconfigure(0, weight=1)
        self.entryfr4.grid_columnconfigure(0, weight=1)
        self.entryfr4.grid_rowconfigure(0, weight=1)
        self.configurarTree_lista_processos_remessa()

        # Rodapé entryfr5:

        #--- acabaram os 'entryfr', apenas código geral para o entryframe a partir daqui ---
        self.entryframe.bind_all("<Command-Escape>", self.fechar_painel_entrada)


    def atualizar_combo_lista_destino(self):
        """ Atualizar a lista de destinatários de remessas na
            combobox correspondente, obtendo info a partir da base de dados.
        """
        fornecedores = db.obter_lista_fornecedores()
        lista_forn = [f"{forn['id']} - {forn['nome']}" for forn in fornecedores]
        self.ef_combo_destino['values'] = lista_forn


    def atualizar_combo_lista_reparacoes(self):
        """ Atualizar a lista de reparações por enviar ou por receber na
            combobox correspondente, obtendo info a partir da base de dados.
        """
        tipo = self.ef_var_tipo.get()
        if tipo == TIPO_REMESSA_RECECAO:
            self.ef_combo_selecionar_rep['values'] = db.obter_lista_processos_por_receber(
            )
        else:
            self.ef_combo_selecionar_rep['values'] = db.obter_lista_processos_por_enviar(
            )

    def configurarTree_lista_processos_remessa(self):
        # Ordenar por coluna ao clicar no respetivo cabeçalho
        for col in self.tree_lista_processos_remessa['columns']:
            self.tree_lista_processos_remessa.heading(col, text=col.title(),
                                                      command=lambda c=col: self.sortBy(self.tree_lista_processos_remessa, c, 0))

        # Barra de deslocação para a tabela
        self.tree_lista_processos_remessa.grid(
            column=0, row=0, sticky=tk.N + tk.W + tk.E, in_=self.ef_lista)
        self.vsb_lista = AutoScrollbar(
            self.ef_lista, orient="vertical", command=self.tree_lista_processos_remessa.yview)
        self.tree_lista_processos_remessa.configure(
            yscrollcommand=self.vsb_lista.set)
        self.vsb_lista.grid(column=1, row=0, sticky=tk.N +
                            tk.S, in_=self.ef_lista)

    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.selectItem_popup)
        self.tree.bind('<Double-1>', lambda x: self.create_window_detalhe_remessa(
            num_remessa=self.remessa_selecionada))
        self.tree.bind("<Button-2>", self.popupMenu)
        self.tree.bind("<Button-3>", self.popupMenu)
        self.update_idletasks()

    def unbind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', None)
        self.tree.bind('<Double-1>', None)
        self.tree.bind("<Button-2>", None)
        self.tree.bind("<Button-3>", None)
        self.update_idletasks()

    def selectItem_popup(self, event):
        """ # Hacking moment: Uma função que junta duas funções, para assegurar a sequência...
        """
        self.selectItem()
        self.popupMenu(event)

    def popupMenu(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        self.selectItem()

        iid = self.tree.identify_row(event.y)
        x, y = event.x_root, event.y_root
        if iid:
            if x != 0 and y != 0:
                # mouse pointer over item
                self.tree.selection_set(iid)
                self.tree.focus(iid)
                self.contextMenu.post(event.x_root, event.y_root)
                print("popupMenu(): x,y = ", event.x_root, event.y_root)
            else:
                print("popupMenu(): wrong values for event - x=0, y=0")
        else:
            print(iid)
            print("popupMenu(): Else - No code here yet! (mouse not over item)")
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
            pass

    def selectItem(self, *event):
        """
        Obter remessa selecionada (após clique de rato na linha correspondente)
        """
        curItem = self.tree.focus()
        tree_linha = self.tree.item(curItem)

        remessa = tree_linha["values"][0]
        destino = tree_linha["values"][2]
        self.my_statusbar.set(f"{remessa} • {destino}")
        self.remessa_selecionada = remessa

    def create_window_detalhe_remessa(self, *event, num_remessa=None):
        if num_remessa is None:
            return
        self.remessa_detail_windows_count += 1
        self.remessa_newDetailsWindow[self.remessa_detail_windows_count] = tk.Toplevel(
        )
        self.remessa_newDetailsWindow[self.remessa_detail_windows_count].title(
            f'Detalhe de remessa: {num_remessa}')
        self.janela_detalhes_remessa = remessaDetailWindow(
            self.remessa_newDetailsWindow[self.remessa_detail_windows_count],
            num_remessa, self.estado_app)

    def liga_desliga_menu_novo(self, *event):
        """
        Liga e desliga menus com base na configuração atual da janela. Por exemplo, ao
        abrir o painel de entrada de dados, desativa o menu "nova remessa", para evitar
        que o painel se feche inadvertidamente.
        """
        if self.is_entryform_visible:
            self.estado_app.main_window.file_menu.entryconfigure("Nova remessa", state="disabled")
            # TODO - corrigir bug: o atalho de teclado só fica realmente inativo depois de acedermos ao menu ficheiro. Porquê??
            self.estado_app.main_window.unbind_all("<Command-r>")
        else:
            self.estado_app.main_window.file_menu.entryconfigure("Nova remessa", state="active")
            self.estado_app.main_window.bind_all("<Command-r>", lambda
                *x: self.estado_app.main_window.create_window_remessas(criar_nova_remessa=True))


    def radio_tipo_command(self, *event):
        """
        Ajustes que devem ocorrer no formulário quando o utilizador altera o
        tipo de remessa.
        """
        tipo = self.ef_var_tipo.get()
        if tipo == TIPO_REMESSA_RECECAO:
            self.ef_lbl_destino.configure(text="Origem:")
            self.str_num_processos = f"Número de processos a receber: {self.num_processos}"
        else:
            self.ef_lbl_destino.configure(text="Destino:")
            self.str_num_processos = f"Número de processos a enviar: {self.num_processos}"
        self.my_statusbar.set(self.str_num_processos)

    def liga_desliga_menu_novo(self, *event):
        """
        Liga e desliga menus com base na configuração atual da janela. Por exemplo, ao
        abrir o painel de entrada de dados, desativa o menu "nova reparação", para evitar
        que o painel se feche inadvertidamente.
        """
        if self.is_entryform_visible == True:
            self.estado_app.main_window.file_menu.entryconfigure("Nova remessa", state="disabled")
            self.estado_app.main_window.unbind_all("<Command-r>")
        else:
            self.estado_app.main_window.file_menu.entryconfigure("Nova remessa", state="active")
            self.estado_app.main_window.bind_all("<Command-r>")

    def clear_text(self):
        self.entryframe.focus()
        self.ef_var_tipo.set(TIPO_REMESSA_ENVIO)
        self.ef_var_destino.set("Selecionar centro técnico...")  # TODO
        self.num_processos = 0
        self.str_num_processos = f"Número de processos a enviar: {self.num_processos}"
        self.my_statusbar.set(self.str_num_processos)
        self.ef_var_reparacoes_a_enviar.set("Selecionar reparações...")

        self.ef_txt_num_reparacao.delete(0, 'end')
        self.tree_lista_processos_remessa.delete(
            *self.tree_lista_processos_remessa.get_children())

    def on_save_remessa(self, event=None):
            # remessa = recolher todos os dados do formulário  #TODO
        remessa = "teste"
        self.ultima_remessa = db.save_remessa(remessa)  # TODO - None se falhar
        if self.ultima_remessa:
            self.on_remessa_save_success()
        else:
            wants_to_try_again_save = messagebox.askquestion(message='Não foi possível guardar esta remessa na base de dados. Deseja tentar novamente?',
                                                             default='yes',
                                                             parent=self)
            if wants_to_try_again_save == 'yes':
                self.on_save_remessa()
            else:
                self.on_remessa_cancel()

    def on_remessa_save_success(self):
        print("Remessa guardada com sucesso")
        # TODO - criar um mecanismo para obter o número da reparação acabada de
        # introduzir na base de dados
        self.ultima_remessa = "333"
        wants_to_print = messagebox.askquestion(message='A remessa foi guardada com sucesso. Deseja imprimir?',
                                                default='yes',
                                                parent=self)
        if wants_to_print == 'yes':
            imprimir.imprimir_guia_de_remessa(self.ultima_remessa)
            self.fechar_painel_entrada()
        else:
            self.fechar_painel_entrada()
            # self.entryframe.focus()

    # TODO
    def on_remessa_cancel(self, event=None):
        # caso haja informação introduzida no formulário TODO: verificar
        # primeiro
        wants_to_cancel = messagebox.askyesno(message='Tem a certeza que deseja cancelar a introdução de dados? Toda a informação não guardada será eliminada de forma irreversível.',
                                              default='no',
                                              parent=self)
        if wants_to_cancel:
            self.fechar_painel_entrada()
        else:
            self.entryframe.focus()

    def inserir_dados_de_exemplo(self):
        for i in range(1, 1002, 3):
            self.tree.insert("", "end", text="", values=(
                str(i), "Loja X", "Fornecedor", "3", "2017-12-31"))
            self.tree.insert("", "end", text="", values=(
                str(i + 1), "Centro técnico", "Loja X", "10", "2017-01-12"))
            self.tree.insert("", "end", text="", values=(
                str(i + 2), "Loja X", "Distribuidor internacional", "10", "2017-02-01"))

