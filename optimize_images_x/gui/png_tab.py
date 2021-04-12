from tkinter import ttk, messagebox
from string import ascii_uppercase, ascii_letters

from pyisemail import is_email

from gui.base_app import baseApp
from gui.extra_tk_utilities import LabelEntry, LabelText
from gui.detalhe_contacto import contactDetailWindow
from global_setup import *
from misc.constants import TODOS_OS_PAISES, TIPO_REP_STOCK
from misc.misc_funcs import check_and_normalize_phone_number, validate_phone_entry


if USE_LOCAL_DATABASE:
    from local_db import db_main as db
else:
    from remote_db import db_main as db


class ContactsWindow(baseApp):
    """ base class for application """


    def __init__(self, master, estado_app, pesquisar, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.estado_app = estado_app
        self.master = master

        # Obtém uma referência para a barra de estado da janela principal,
        # para poder utilizar a barra de progresso nessa janela.
        self.main_statusbar = estado_app.main_window.my_statusbar
        self.main_statusbar.show_progress(value=50, mode="determinate")
        self.contacto_newDetailsWindow = {}
        self.contact_detail_windows_count = 0
        self.contacto_selecionado = None
        self.ultimo_contacto = None
        self.ncontactos = 0
        self.last_selected_view_contacts_list = "Clientes"  # ou "Fornecedores"
        self.new_contact_telefone = ""
        self.new_contact_telemovel = ""
        self.new_contact_tel_emp = ""

        self.master.minsize(CONTACTOS_MIN_WIDTH, CONTACTOS_MIN_HEIGHT)
        self.master.maxsize(CONTACTOS_MAX_WIDTH, CONTACTOS_MAX_HEIGHT)

        width, height = self.screen_size()
        main_width = self.estado_app.main_window.master.winfo_width()

        if width - CONTACTOS_MIN_WIDTH < main_width:
            pos_x = width - CONTACTOS_MIN_WIDTH
        else:
            pos_x = main_width + 1

        if height < (CONTACTOS_MIN_HEIGHT + 92):
            pos_y = height - CONTACTOS_MIN_HEIGHT - 22
        else:
            pos_y = 92

        self.master.geometry(f'{CONTACTOS_MIN_WIDTH}x{CONTACTOS_MIN_HEIGHT}+{pos_x}+{pos_y}')
        self.master.title("Contactos")

        self.montar_barra_de_ferramentas()
        self.montar_tabela()
        self.gerar_menu()

        self.gerar_painel_entrada()
        self.frames = self.composeFrames()
        self.main_statusbar.hide_progress(last_update=100)
        self.my_statusbar.show_progress(value=30, length=60, mode="determinate")
        clientes = db.obter_clientes()
        self.my_statusbar.progress_update(70)
        self.atualizar_lista(clientes)
        self.my_statusbar.hide_progress(last_update=100)

        if self.estado_app.painel_novo_contacto_aberto:
            self.mostrar_painel_entrada()
        if pesquisar:
            self.clique_a_pesquisar()


    def contar_linhas(self):
        """ Obtém o número de linhas da tabela de contactos. """
        linhas = self.tree.get_children("")
        return len(linhas)


    def atualizar_soma(self):
        """
        Atualiza a barra de estado com o número de contactos.
        """
        self.ncontactos = self.contar_linhas()
        self.my_statusbar.set(f"{self.ncontactos} contactos")


    def gerar_menu(self):
        self.menu = tk.Menu(self.master)
        # ----------------Menu contextual tabela principal---------------------
        self.contextMenu = tk.Menu(self.menu)
        self.contextMenu.add_command(label="Informações",
                                     command=lambda: self.create_window_detalhe_contacto(
                                         num_contacto=self.contacto_selecionado))
        # self.contextMenu.add_command(label="Abrir no site da transportadora", command=self.abrir_url_browser)
        self.contextMenu.add_separator()
        # self.contextMenu.add_command(label="Copiar número de objeto", command=self.copiar_obj_num)
        # self.contextMenu.add_command(label="Copiar mensagem de expedição", command=self.copiar_msg)
        # self.contextMenu.add_separator()
        # self.contextMenu.add_command(label="Arquivar/restaurar remessa", command=self.del_remessa)
        # self.contextMenu.add_separator()
        # self.contextMenu.add_command(label="Registar cheque recebido", command=self.pag_recebido)
        # self.contextMenu.add_command(label="Registar cheque depositado", command=self.chq_depositado)


    def montar_tabela(self):
        self.tree = ttk.Treeview(
            self.leftframe, height=60, selectmode='browse')
        self.tree['columns'] = ('ID', 'Nome', 'Telefone', 'Email')
        self.tree.pack(side=tk.TOP, fill=tk.BOTH)
        self.tree.column('#0', anchor=tk.W, minwidth=0, stretch=0, width=0)
        self.tree.column('ID', anchor=tk.E, minwidth=37, stretch=0, width=37)
        self.tree.column('Nome', minwidth=140, stretch=1, width=140)
        self.tree.column('Telefone', anchor=tk.E,
                         minwidth=90, stretch=1, width=90)
        self.tree.column('Email', anchor=tk.E,
                         minwidth=130, stretch=1, width=130)

        self.configurarTree()

        self.leftframe.grid_columnconfigure(0, weight=1)
        self.leftframe.grid_rowconfigure(0, weight=1)
        self.bind_tree()


    def montar_barra_de_ferramentas(self):
        self.btn_clientes = ttk.Button(
            self.topframe, style="secondary.TButton", text="Clientes",
            command=self.mostrar_clientes)
        self.btn_clientes.grid(column=0, row=0)
        self.dicas.bind(self.btn_clientes, 'Mostrar apenas clientes.')

        self.btn_fornecedores = ttk.Button(
            self.topframe, style="secondary.TButton", text="Fornecedores",
            command=self.mostrar_fornecedores)
        self.btn_fornecedores.grid(column=1, row=0)
        self.dicas.bind(self.btn_fornecedores,
                        'Mostrar apenas fornecedores\ne centros técnicos.')

        self.btn_add = ttk.Button(
            self.topframe, text=" ➕", style="secondary.TButton", width=3,
            command=self.show_entryform)
        self.btn_add.grid(column=3, row=0)
        self.dicas.bind(self.btn_add, 'Criar novo contacto.')

        self.text_input_pesquisa = ttk.Entry(self.topframe, width=12)
        self.text_input_pesquisa.grid(column=4, row=0)
        self.dicas.bind(self.text_input_pesquisa,
                        'Para iniciar a pesquisa, digite\numa palavra ou frase. (⌘F)')

        letras_etc = ascii_letters + "01234567890-., "
        for char in letras_etc:
            keystr = '<KeyRelease-' + char + '>'
            self.text_input_pesquisa.bind(keystr, self.mostrar_pesquisa)
        self.text_input_pesquisa.bind('<Button-1>', self.clique_a_pesquisar)
        self.text_input_pesquisa.bind('<KeyRelease-Escape>', self.cancelar_pesquisa)
        self.text_input_pesquisa.bind('<Command-a>',
                                      lambda x: self.text_input_pesquisa.select_range(0, tk.END))

        for col in range(1, 4):
            self.topframe.columnconfigure(col, weight=0)
        self.topframe.columnconfigure(2, weight=1)


    def mostrar_painel_entrada(self, *event):
        self.estado_app.painel_novo_contacto_aberto = True
        self.show_entryform()
        self.ef_ltxt_nome.entry.focus()
        self.liga_desliga_menu_novo()


    def fechar_painel_entrada(self, *event):
        self.estado_app.painel_novo_contacto_aberto = False
        self.clear_text()
        self.hide_entryform()
        self.liga_desliga_menu_novo()


    def clear_text(self):
        self.entryframe.focus()
        self.ef_var_tipo_is_cliente.set(True)
        self.ef_var_tipo_is_fornecedor.set(False)
        # self.ef_var_tipo_is_loja.set(False)
        self.ef_combo_pais.current(178)

        widgets = (self.ef_ltxt_nome,
                   self.ef_ltxt_empresa,
                   self.ef_ltxt_nif,
                   self.ef_ltxt_telefone,
                   self.ef_ltxt_tlm,
                   self.ef_ltxt_tel_empresa,
                   self.ef_ltxt_email,
                   self.ef_lstxt_morada,
                   self.ef_ltxt_cod_postal,
                   self.ef_ltxt_localidade,
                   self.ef_lstxt_notas)
        for widget in widgets:
            widget.clear()


    def gerar_painel_entrada(self):

        # entryfr1-----------------------------
        # TODO:adicionar campos, notebook, etc
        # criar funções para usar esses campos, ora para adicionar, ora para
        # editar, ora para visualizar registos

        self.ef_var_tipo_is_cliente = tk.IntVar()
        self.ef_var_tipo_is_cliente.set(True)
        self.ef_var_tipo_is_fornecedor = tk.IntVar()
        if self.estado_app.tipo_novo_contacto == "Fornecedor":
            self.ef_var_tipo_is_fornecedor.set(True)
            self.ef_var_tipo_is_cliente.set(False)
        # self.ef_var_tipo_is_loja = tk.IntVar()

        self.ef_cabecalho = ttk.Frame(self.entryfr1, padding=4)
        self.ef_lbl_titulo = ttk.Label(
            self.ef_cabecalho, style="Panel_Title.TLabel", text="Adicionar Contacto:")
        self.ef_lbl_tipo = ttk.Label(
            self.ef_cabecalho, text="Tipo:", style="Panel_Body.TLabel")

        self.ef_chkbtn_tipo_cliente = ttk.Checkbutton(
            self.ef_cabecalho, text="Cliente", style="Panel_Body.Checkbutton",
            variable=self.ef_var_tipo_is_cliente)
        self.ef_chkbtn_tipo_fornecedor = ttk.Checkbutton(
            self.ef_cabecalho, text="Fornecedor ou centro técnico", style="Panel_Body.Checkbutton",
            variable=self.ef_var_tipo_is_fornecedor)
        # self.ef_chkbtn_tipo_loja = ttk.Checkbutton(self.ef_cabecalho, text="Loja do nosso grupo", style="Panel_Body.Checkbutton", variable=self.ef_var_tipo_is_loja)

        self.btn_adicionar = ttk.Button(self.ef_cabecalho, default="active",
                                        style="Active.TButton", text="Adicionar",
                                        command=self._on_save_contact)
        self.btn_cancelar = ttk.Button(
            self.ef_cabecalho, text="Cancelar", command=self.on_contact_cancel)

        self.ef_lbl_titulo.grid(column=0, row=0, columnspan=3, sticky='width', pady="0 10")
        self.ef_lbl_tipo.grid(column=0, row=1, sticky='e')
        self.ef_chkbtn_tipo_cliente.grid(column=1, row=1, sticky='width')
        self.ef_chkbtn_tipo_fornecedor.grid(column=1, row=2, sticky='width')
        # self.ef_chkbtn_tipo_loja.grid(column=1, row=3, sticky='width')

        self.btn_adicionar.grid(column=3, row=1, sticky='we')
        self.btn_cancelar.grid(column=3, row=2, sticky='we')

        self.ef_cabecalho.grid(column=0, row=0, sticky='we')
        self.entryfr1.columnconfigure(0, weight=1)
        self.ef_cabecalho.columnconfigure(2, weight=1)

        # self.btn_adicionar.bind('<Button-1>', self.add_remessa)

        # entryfr2-----------------------------
        self.ef_lf_top = ttk.Labelframe(self.entryfr2, padding=4, text="")
        self.ef_ltxt_nome = LabelEntry(self.ef_lf_top, "Nome", style="Panel_Body.TLabel")
        self.ef_ltxt_empresa = LabelEntry(self.ef_lf_top, "Empresa", style="Panel_Body.TLabel")
        self.ef_ltxt_nif = LabelEntry(self.ef_lf_top, "NIF", style="Panel_Body.TLabel")
        self.ef_ltxt_nif.bind("<FocusOut>", self.validar_nif)

        self.ef_ltxt_telefone = LabelEntry(self.ef_lf_top, "\nTel.", width=14,
                                           style="Panel_Body.TLabel")
        self.ef_ltxt_tlm = LabelEntry(self.ef_lf_top, "\nTlm.", width=14, style="Panel_Body.TLabel")
        self.ef_ltxt_tel_empresa = LabelEntry(self.ef_lf_top, "\nTel. empresa", width=14,
                                              style="Panel_Body.TLabel")
        self.ef_ltxt_telefone.entry.bind("<FocusOut>", self._on_tel_exit)
        self.ef_ltxt_tlm.entry.bind("<FocusOut>", self._on_tel_exit)
        self.ef_ltxt_tel_empresa.entry.bind("<FocusOut>", self._on_tel_exit)

        self.ef_ltxt_email = LabelEntry(self.ef_lf_top, "Email", style="Panel_Body.TLabel")
        self.ef_lstxt_morada = LabelText(self.ef_lf_top, "\nMorada", height=2,
                                         style="Panel_Body.TLabel")

        self.ef_ltxt_cod_postal = LabelEntry(self.ef_lf_top, "Código Postal",
                                             style="Panel_Body.TLabel")
        self.ef_ltxt_localidade = LabelEntry(self.ef_lf_top, "Localidade",
                                             style="Panel_Body.TLabel")

        self.ef_lbl_pais = ttk.Label(self.ef_lf_top, text="País", style="Panel_Body.TLabel")
        self.paises_value = tk.StringVar()
        self.ef_combo_pais = ttk.Combobox(self.ef_lf_top, values=TODOS_OS_PAISES,
                                          textvariable=self.paises_value,
                                          state='readonly')
        self.ef_combo_pais.current(178)
        self.ef_combo_pais.bind("<Key>", self.procurar_em_combobox)

        self.ef_lstxt_notas = LabelText(self.ef_lf_top, "\nNotas:", height=3,
                                        style="Panel_Body.TLabel")

        self.ef_ltxt_nome.grid(column=0, row=0, columnspan=3, padx=5, sticky='we')
        self.ef_ltxt_empresa.grid(column=0, row=1, columnspan=2, padx=5, sticky='we')
        self.ef_ltxt_nif.grid(column=2, row=1, padx=5, sticky='we')

        self.ef_ltxt_telefone.grid(column=0, row=2, padx=5, sticky='we')
        self.ef_ltxt_tlm.grid(column=1, row=2, padx=5, sticky='we')
        self.ef_ltxt_tel_empresa.grid(column=2, row=2, padx=5, sticky='we')
        self.ef_ltxt_email.grid(column=0, row=3, columnspan=3, padx=5, sticky='we')
        self.ef_lstxt_morada.grid(column=0, row=4, columnspan=3, rowspan=2, padx=5, sticky='we')

        self.ef_ltxt_cod_postal.grid(column=0, row=6, padx=5, sticky='we')
        self.ef_ltxt_localidade.grid(column=1, row=6, columnspan=2, padx=5, sticky='we')

        self.ef_lbl_pais.grid(column=0, columnspan=3, row=7, padx=5, sticky='we')
        self.ef_combo_pais.grid(column=0, columnspan=3, row=8, padx=5, sticky='we')
        self.ef_lstxt_notas.grid(column=0, row=9, columnspan=3, rowspan=4, padx=5, sticky='we')

        self.ef_lf_top.grid(column=0, row=0, sticky='we')
        self.ef_lf_top.columnconfigure(0, weight=1)
        self.ef_lf_top.columnconfigure(1, weight=1)
        self.ef_lf_top.columnconfigure(2, weight=1)
        self.entryfr2.columnconfigure(0, weight=1)

        # --- acabaram os 'entryfr', apenas código geral para o entryframe a partir daqui ---
        self.entryframe.bind_all("<Command-Escape>", self.fechar_painel_entrada)


    def procurar_em_combobox(self, event):
        """
        Saltar para o primeiro país da lista (combobox) começado pela letra
        correspondente à tecla pressionada.
        """
        tecla_pressionada = event.char.upper()
        if tecla_pressionada in ascii_uppercase:
            for index, pais in enumerate(TODOS_OS_PAISES):
                if pais[0] == tecla_pressionada:
                    self.ef_combo_pais.current(index)
                    break


    def mostrar_fornecedores(self, *event):
        self.master.title("Fornecedores")
        self.last_selected_view_contacts_list = "Fornecedores"
        self.my_statusbar.clear()
        self.my_statusbar.show_progress(value=30, length=60, mode="determinate")
        fornecedores = db.obter_fornecedores()
        self.my_statusbar.progress_update(70)
        self.atualizar_lista(fornecedores)
        self.my_statusbar.hide_progress(last_update=100)


    def mostrar_clientes(self, *event):
        self.master.title("Clientes")
        self.last_selected_view_contacts_list = "Clientes"
        self.my_statusbar.show_progress(value=30, length=60, mode="determinate")
        clientes = db.obter_clientes()
        self.my_statusbar.progress_update(70)
        self.atualizar_lista(clientes)
        self.my_statusbar.hide_progress(last_update=100)


    def after_adicionar_contacto(self, *event):
        """ Este médodo é executado após guardar com sucesso um contacto. Caso
            o utilizador esteja a criar uma reparação, adiciona o contacto ao
            campo correspondente.
        """
        if self.estado_app.tipo_novo_contacto == "Cliente":
            self.estado_app.contacto_para_nova_reparacao = self.ultimo_contacto
            if self.estado_app.painel_nova_reparacao_aberto:
                self.estado_app.main_window.close_window_contactos()
            else:
                wants_to_create = messagebox.askquestion(
                    message='O novo cliente foi guardado com sucesso. Deseja criar uma nova reparação?',
                    default='yes',
                    parent=self)
                if wants_to_create == 'yes':
                    self.estado_app.contacto_para_nova_reparacao = self.ultimo_contacto
                    self.estado_app.main_window.mostrar_painel_entrada()
                self.mostrar_clientes()
        elif self.estado_app.tipo_novo_contacto == "Fornecedor":
            self.estado_app.contacto_para_nova_reparacao = self.ultimo_contacto
            if self.estado_app.painel_nova_reparacao_aberto:
                self.estado_app.main_window.close_window_contactos()
            else:
                wants_to_create = messagebox.askquestion(
                    message='O novo fornecedor foi guardado com sucesso. Deseja criar uma nova reparação?',
                    default='yes',
                    parent=self)
                if wants_to_create == 'yes':
                    self.estado_app.contacto_para_nova_reparacao = self.ultimo_contacto
                    self.estado_app.main_window.mostrar_painel_entrada()
                    self.estado_app.main_window.ef_var_tipo.set(TIPO_REP_STOCK)
                    self.estado_app.main_window.radio_tipo_command()
                self.mostrar_fornecedores()
        else:
            self.mostrar_clientes()  # atualizar a lista de contactos nesta janela fechar o formulário


    def bind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', self.selectItem_popup)
        self.tree.bind('<Double-1>', lambda x: self.create_window_detalhe_contacto(
            num_contacto=self.contacto_selecionado))
        self.tree.bind("<Button-2>", self.popupMenu)
        self.tree.bind("<Button-3>", self.popupMenu)


    def unbind_tree(self):
        self.tree.bind('<<TreeviewSelect>>', None)
        self.tree.bind('<Double-1>', None)
        self.tree.bind("<Button-2>", None)
        self.tree.bind("<Button-3>", None)


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
        Obter contacto selecionado (após clique de rato na linha correspondente)
        """
        curItem = self.tree.focus()
        tree_linha = self.tree.item(curItem)

        contacto = tree_linha["values"][0]
        nome = tree_linha["values"][1]
        self.my_statusbar.set(f"{contacto} • {nome}")
        self.contacto_selecionado = contacto


    def create_window_detalhe_contacto(self, *event, num_contacto=None):
        if num_contacto is None:
            return
        self.contact_detail_windows_count += 1
        self.contacto_newDetailsWindow[self.contact_detail_windows_count] = tk.Toplevel(
        )
        self.contacto_newDetailsWindow[self.contact_detail_windows_count].title(
            f'Detalhe de contacto: {num_contacto}')
        self.janela_detalhes_contacto = contactDetailWindow(
            self.contacto_newDetailsWindow[self.contact_detail_windows_count],
            num_contacto,
            self.estado_app)
        self.contacto_newDetailsWindow[self.contact_detail_windows_count].focus()


    def liga_desliga_menu_novo(self, *event):
        """
        Liga e desliga menus com base na configuração atual da janela. Por exemplo, ao
        abrir o painel de entrada de dados, desativa o menu "novo contacto", para evitar
        que o painel se feche inadvertidamente.
        """
        if self.is_entryform_visible:
            self.estado_app.main_window.file_menu.entryconfigure("Novo contacto",
                                                                 state="disabled")
            # TODO - corrigir bug: o atalho de teclado só fica realmente inativo depois de acedermos ao menu ficheiro. Porquê??
            self.estado_app.main_window.unbind_all("<Command-t>")
        else:
            self.estado_app.main_window.file_menu.entryconfigure("Novo contacto",
                                                                 state="active")
            self.estado_app.main_window.bind_all("<Command-t>", lambda
                *x: self.estado_app.main_window.create_window_contacts(
                criar_novo_contacto="Cliente"))


    def _on_save_contact(self, event=None):
        """ Recolhe todos os dados do formulário e guarda um novo contacto"""

        if not self._is_form_data_valid():
            return

        new_contact = {
            'nome': self.ef_ltxt_nome.get(),
            'empresa': self.ef_ltxt_empresa.get(),
            'telefone': self.new_contact_telefone,
            'telemovel': self.new_contact_telemovel,
            'telefone_empresa': self.new_contact_tel_emp,
            'email': self.ef_ltxt_email.get(),
            'morada': self.ef_lstxt_morada.get(),
            'cod_postal': self.ef_ltxt_cod_postal.get(),
            'localidade': self.ef_ltxt_localidade.get(),
            'pais': self.ef_combo_pais.get(),
            'nif': self.ef_ltxt_nif.get(),
            'notas': self.ef_lstxt_notas.get(),
            'is_cliente': self.ef_var_tipo_is_cliente.get(),
            'is_fornecedor': self.ef_var_tipo_is_fornecedor.get(),
            'criado_por_utilizador_id': self.estado_app.main_window.user_id,
        }

        self.ultimo_contacto = db.save_contact(new_contact)


        print("self.ultimo_contacto:", self.ultimo_contacto )
        print("new_contact:", new_contact)


        if new_contact['is_cliente']:
            self.estado_app.tipo_novo_contacto = "Cliente"
        elif new_contact['is_fornecedor']:
            self.estado_app.tipo_novo_contacto = "Fornecedor"

        if self.ultimo_contacto:
            self._on_contact_save_success()
        else:
            wants_to_try_again_save = messagebox.askquestion(message='Não foi possível guardar este contacto na base de dados. Pretende tentar novamente?',
                                                             default='yes',
                                                             parent=self)
            if wants_to_try_again_save == 'yes':
                self._on_save_contact()
            else:
                self.on_contact_cancel()


    def _on_contact_save_success(self):
        self.fechar_painel_entrada()
        self.after_adicionar_contacto()
        self.ultimo_contacto = None


    # TODO
    def on_contact_cancel(self, event=None):
        # caso haja informação introduzida no formulário TODO: verificar
        # primeiro
        wants_to_cancel = messagebox.askyesno(
            message='Tem a certeza que deseja cancelar a introdução de dados? Toda a informação não guardada será eliminada de forma irreversível.',
            default='no',
            parent=self)
        if wants_to_cancel:
            self.fechar_painel_entrada()
        else:
            self.entryframe.focus()


    def inserir_contacto(self, contact_num=0, nome="", telefone="", email=""):
        """ Adicionar umo contacto à lista, na tabela principal.
        """
        self.tree.insert("", "end", values=(str(contact_num), nome,
                                            telefone, email))


    def atualizar_lista(self, contactos):
        """ Atualizar a lista de reparações na tabela principal.
        """
        for i in self.tree.get_children():  # Limpar tabela primeiro
            self.tree.delete(i)

        for contacto in contactos:
            self.inserir_contacto(contact_num=contacto['id'],
                                  nome=contacto['nome'],
                                  telefone=contacto['telefone'],
                                  email=contacto['email'])

        self.atualizar_soma()
        self.alternar_cores(self.tree)


    def clique_a_pesquisar(self, *event):
        self.text_input_pesquisa.focus_set()
        self.my_statusbar.set("Por favor, introduza o texto a pesquisar na base de dados.")


    def cancelar_pesquisa(self, event):
        self.tree.focus_set()
        if self.last_selected_view_contacts_list == "Clientes":
            self.mostrar_clientes()
        else:
            self.mostrar_fornecedores()


    def mostrar_pesquisa(self, *event):
        termo_pesquisa = self.text_input_pesquisa.get()
        termo_pesquisa = termo_pesquisa.strip()

        # regressar ao campo de pesquisa caso não haja texto a pesquisar (resolve questão do atalho de teclado)
        if termo_pesquisa == "":
            if self.last_selected_view_contacts_list == "Clientes":
                contactos = db.obter_clientes()
            else:
                contactos = db.obter_fornecedores()
            self.atualizar_lista(contactos)
            return
        elif (len(termo_pesquisa) < 3) and not self.isNumeric(termo_pesquisa):
            return

        self.my_statusbar.show_progress(value=30, length=60, mode="determinate")
        # self.my_statusbar.set(f"A pesquisar: {termo_pesquisa}")

        # Pesquisar filtrando pelo tipo de contacto selecionado (cliente/fornecedor)
        contactos = db.pesquisar_contactos(termo_pesquisa,
                                           tipo=self.last_selected_view_contacts_list)
        self.my_statusbar.progress_update(70)
        self.atualizar_lista(contactos)
        self.ncontactos = len(contactos)
        self.my_statusbar.hide_progress(last_update=100)

        if self.ncontactos == 0:
            s_status = f"""Pesquisa: {'"'+termo_pesquisa.upper()+'"'}. Não foram encontrados contactos."""
        else:
            s_status = f"""Pesquisa: {'"'+termo_pesquisa.upper()+'"'}. Encontrados {self.ncontactos} contactos."""
        self.my_statusbar.set(s_status)


    def validar_nif(self, *event):
        """ Verifica se já existe na base de dados um contacto criado com o NIF
            indicado. Se existir, propor abrir a janela de detalhes. Se não
            existir, continuar a criar o novo contacto.
        """

        nif = self.ef_ltxt_nif.get().strip()
        if nif:
            contacto = db.contact_exists(nif)
        else:
            contacto = None

        if contacto:
            msg = f"Já existe na base de dados um contacto com o NIF indicado ({contacto['id']} " \
                  f"- {contacto['nome']}). Pretende verificar o contacto existente?"
            verificar = messagebox.askquestion(message=msg, default='yes', parent=self)
            if verificar == 'yes':
                self.create_window_detalhe_contacto(num_contacto=contacto['id'])

    def _on_tel_exit(self, event):
        validate_phone_entry(self, event.widget)


    def _validar_telefones(self, *event) -> bool:
            self.new_contact_telemovel = ""
            self.new_contact_telefone = ""
            self.new_contact_tel_emp = ""

            try:
                self.new_contact_telefone = check_and_normalize_phone_number(self.ef_ltxt_telefone.get()).replace(" ","")
            except Exception as e:
                pass

            try:
                self.new_contact_telemovel = check_and_normalize_phone_number(self.ef_ltxt_tlm.get()).replace(" ", "")
            except Exception as e:
                pass

            try:
                self.new_contact_tel_emp = check_and_normalize_phone_number(self.ef_ltxt_tel_empresa.get()).replace(" ", "")
            except Exception as e:
                pass

            # Verificar já se temos pelo menos um contacto telefónico
            if (self.new_contact_telefone
                 or self.new_contact_telemovel
                 or self.new_contact_tel_emp):
                return True
            else:
                return False


    def _is_form_data_valid(self) -> bool:
        """ Verifica se todos os campos obrigatórios foram preenchidos e se os
            dados introduzidos estão corretos.
        """
        if not self.ef_ltxt_nome.get().strip():
            msg = 'O campo "Nome" é de preenchimento obrigatório.'
            messagebox.showwarning(message=msg, parent=self)
            self.ef_ltxt_nome.entry.focus()
            return False
        elif not self._validar_telefones():
            msg = 'Deverá indicar, pelo menos, um número de contacto telefónico.'
            messagebox.showwarning(message=msg, parent=self)
            return False
        elif not is_email(self.ef_ltxt_email.get().strip()):
            msg = 'O endereço de email introduzido não parece ser válido.'
            messagebox.showwarning(message=msg, parent=self)
            self.ef_ltxt_email.entry.focus()
            return False
        elif not (self.ef_var_tipo_is_cliente.get()
                  or self.ef_var_tipo_is_fornecedor.get()):
            msg = 'Por favor, especifique qual a categoria (cliente/fornecedor) a atribuir a este contacto.'
            messagebox.showwarning(message=msg, parent=self)
            self.ef_chkbtn_tipo_cliente.focus()
            return False
        else:
            return True
