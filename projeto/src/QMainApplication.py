import sys
from decimal import Decimal
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QStackedWidget,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


# Importa todas as funções (Views, Functions e Procedures) do conexao:
from conexao import (
    vw_vendas_recentes,              # Presente na página vendas
    vw_geral_estoque_produtos,       # Presente na página vendas
    vw_estoque_critico,              # Presente na página vendas
    vw_resumo_caixa_diario,          # Presente na página vendas

    fn_autenticar_funcionario,       # Presente na página de cadastro / login
    fn_status_produto,               # Presente na página produto
    fn_calcular_pontos_compra,       # Presente na página cliente

    cadastrar_cliente,               # Presente na página de cadastro / login
    registrar_funcionarios,          # Presente na página de cadastro / login
    registrar_venda,                 # Presente na página vendas
    testar_conexao,                  # Presente na página main, venda e cadastro / login

    app_buscar_funcionario_por_cpf,
)


# Sessão:
class SessaoUsuario:
    _usuario_atual = None

    @classmethod
    def iniciar_sessao(cls, dados_usuario):
        """Guarda os dados do funcionário logado."""
        cls._usuario_atual = dados_usuario

    @classmethod
    def obter_usuario(cls):
        """Retorna os dados do usuário atual."""
        return cls._usuario_atual

    @classmethod
    def encerrar_sessao(cls):
        """Limpa os dados ao fazer logout."""
        cls._usuario_atual = None


class TelaCadastro(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__(parent)
        self.stack = stack

        # Layout da janela:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        frame = QFrame()
        frame.setFixedSize(657, 588)
        frame.setObjectName("cadastro")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 18, 25, 20)
        frame_layout.setSpacing(15)

        # Os widgets:
        titulo = QLabel("Cadastro")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuário")
        self.usuario.setMinimumHeight(45)

        self.cpf = QLineEdit()
        self.cpf.setPlaceholderText("CPF")

        self.telefone = QLineEdit()
        self.telefone.setPlaceholderText("Telefone")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-mail")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.EchoMode.Password)

        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.setMinimumHeight(45)
        botao_cadastrar.clicked.connect(self.realizar_cadastro)

        botao_ir_login = QPushButton("Já tenho conta")
        botao_ir_login.clicked.connect(self.ir_para_login)

        # Adiciona cada widget ao frame_layout e, ao final, adiciona o frame ao layout.
        for widget in (
            titulo,
            self.usuario,
            self.cpf,
            self.telefone,
            self.email,
            self.senha,
            botao_cadastrar,
            botao_ir_login,
        ):
            frame_layout.addWidget(widget)

        layout.addWidget(frame)

    # Ações:
    def realizar_cadastro(self):
        nome = self.usuario.text().strip()
        cpf = self.cpf.text().strip()
        telefone = self.telefone.text().strip()
        email = self.email.text().strip()
        senha = self.senha.text().strip()

        if not nome or not cpf or not senha:
            QMessageBox.warning(
                self,
                "Cadastro",
                "Preencha pelo menos Nome, CPF e Senha."
            )
            return

        try:
            sucesso, mensagem = registrar_funcionarios(
                nomeUsuario=nome,
                nomeApelido=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                senha=senha,
            )

            if not sucesso:
                QMessageBox.critical(self, "Erro ao Cadastrar", mensagem)
                return

            QMessageBox.information(
                self,
                "Cadastro",
                "Funcionário cadastrado com sucesso!"
            )

            self.usuario.clear()
            self.cpf.clear()
            self.email.clear()
            self.telefone.clear()
            self.senha.clear()

            self.stack.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(
                self,
                "SQLAlchemy",
                f"Não foi possível registrar: {e}"
            )

    def ir_para_login(self):
        self.stack.setCurrentIndex(1)


class TelaLogin(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__(parent)
        self.stack = stack

        # Layout da janela:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        frame = QFrame()
        frame.setFixedSize(657, 588)
        frame.setObjectName("login")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 18, 25, 20)
        frame_layout.setSpacing(15)

        # Os widgets:
        titulo = QLabel("Login")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        self.cpf = QLineEdit()
        self.cpf.setPlaceholderText("CPF")
        self.cpf.setMinimumHeight(45)

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.EchoMode.Password)

        botao_entrar = QPushButton("Entrar")
        botao_entrar.setMinimumHeight(45)
        botao_entrar.clicked.connect(self.realizar_login)

        botao_ir_cadastro = QPushButton("Cadastrar Funcionário")
        botao_ir_cadastro.clicked.connect(self.ir_para_cadastro)

        # Adiciona cada widget ao frame_layout e, ao final, adiciona o frame ao layout.
        for widget in (
            titulo,
            self.cpf,
            self.senha,
            botao_entrar,
            botao_ir_cadastro,
        ):
            frame_layout.addWidget(widget)

        layout.addWidget(frame)

    # Ações:
    def realizar_login(self):
        cpf = self.cpf.text().strip()
        senha = self.senha.text().strip()

        if not cpf or not senha:
            QMessageBox.warning(
                self,
                "Login",
                "Preencha o CPF e a senha."
            )
            return

        try:
            autenticado = fn_autenticar_funcionario(cpf, senha)

            if not autenticado:
                QMessageBox.warning(
                    self,
                    "Login",
                    "Credenciais incorretas."
                )
                return

            dados_usuario = app_buscar_funcionario_por_cpf(cpf)

            if not dados_usuario:
                QMessageBox.critical(
                    self,
                    "Login",
                    "Autenticação realizada, mas não foi possível "
                    "carregar os dados do funcionário."
                )
                return

            SessaoUsuario.iniciar_sessao(dados_usuario)

            self.cpf.clear()
            self.senha.clear()

            self.stack.setCurrentIndex(2)

            QMessageBox.information(
                self,
                "Login",
                "Login realizado com sucesso!"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro de Login",
                f"Não foi possível realizar o login: {e}"
            )

    def ir_para_cadastro(self):
        self.stack.setCurrentIndex(0)


class TelaEstatisticas(QWidget):
    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título da Página
        titulo = QLabel("📊 Painel de Estatísticas e Desempenho")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Layout com os Cards/Métricas de Estatísticas Resumidas
        cards_layout = QHBoxLayout()

        self.card_vendas = self.criar_card("Total Vendas Recentes", "0")
        self.card_caixa = self.criar_card("Resumo do Caixa", "R$ 0,00")
        self.card_estoque = self.criar_card("Alertas de Estoque Crítico", "0")

        cards_layout.addWidget(self.card_vendas)
        cards_layout.addWidget(self.card_caixa)
        cards_layout.addWidget(self.card_estoque)

        layout.addLayout(cards_layout)

        # Tabela com o resumo geral do estoque / produtos
        label_tabela = QLabel("Visão Geral do Estoque (vw_geral_estoque_produtos):")
        label_tabela.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label_tabela)

        self.tabela_geral = QTableWidget()
        self.tabela_geral.setColumnCount(4)
        self.tabela_geral.setHorizontalHeaderLabels(
            ["ID", "Produto", "Quantidade", "Preço"]
        )
        layout.addWidget(self.tabela_geral)

        # Botões de Ação
        botoes_layout = QHBoxLayout()

        btn_atualizar = QPushButton("🔄 Atualizar Estatísticas")
        btn_atualizar.setMinimumHeight(40)
        btn_atualizar.clicked.connect(self.carregar_dados_estatisticas)

        btn_voltar = QPushButton("⬅ Voltar ao Menu Principal")
        btn_voltar.setMinimumHeight(40)
        btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))

        botoes_layout.addWidget(btn_atualizar)
        botoes_layout.addWidget(btn_voltar)

        layout.addLayout(botoes_layout)
        self.setStyleSheet("background-color: #7b95a6; color: white;")

        # Carrega as estatísticas ao inicializar
        self.carregar_dados_estatisticas()

    def criar_card(self, titulo, valor_inicial):
        """Cria um card visual estilizado para exibir métricas."""
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: #d8e2e8; border-radius: 8px; color: #333333;"
        )
        card_layout = QVBoxLayout(frame)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_valor = QLabel(valor_inicial)
        lbl_valor.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setObjectName("valor")

        card_layout.addWidget(lbl_titulo)
        card_layout.addWidget(lbl_valor)

        return frame

    def atualizar_valor_card(self, card_widget, novo_valor):
        lbl_valor = card_widget.findChild(QLabel, "valor")
        if lbl_valor:
            lbl_valor.setText(str(novo_valor))

    def carregar_dados_estatisticas(self):
        """Consulta as views e atualiza as estatísticas na tela."""
        # 1. Total de Vendas Recentes
        try:
            dados_vendas = (
                vw_vendas_recentes()
                if "vendas_recentes" in globals()
                else vw_vendas_recentes()
            )
            qtd_vendas = len(dados_vendas) if dados_vendas else 0
            self.atualizar_valor_card(self.card_vendas, str(qtd_vendas))
        except Exception as e:
            self.atualizar_valor_card(self.card_vendas, "Erro")

        # 2. Resumo de Caixa
        try:
            resumo_caixa = vw_resumo_caixa_diario()
            self.atualizar_valor_card(
                self.card_caixa,
                str(resumo_caixa) if resumo_caixa else "R$ 0,00",
            )
        except Exception as e:
            self.atualizar_valor_card(self.card_caixa, "Erro")

        # 3. Alertas de Estoque Crítico
        try:
            dados_critico = vw_estoque_critico()
            qtd_critico = len(dados_critico) if dados_critico else 0
            self.atualizar_valor_card(self.card_estoque, str(qtd_critico))
        except Exception as e:
            self.atualizar_valor_card(self.card_estoque, "Erro")

        # 4. Tabela de Geral de Estoque
        try:
            dados_geral = vw_geral_estoque_produtos()
            if dados_geral:
                self.tabela_geral.setRowCount(len(dados_geral))
                for row_idx, row_data in enumerate(dados_geral):
                    for col_idx, valor in enumerate(row_data):
                        self.tabela_geral.setItem(
                            row_idx, col_idx, QTableWidgetItem(str(valor))
                        )
        except Exception as e:
            print(f"Erro ao carregar dados da tabela geral de estoque: {e}")


# --- SUBMENU 1: VENDAS ---
class TelaVendas(QWidget):

  def __init__(self, sub_stack):
    super().__init__()
    self.sub_stack = sub_stack
    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)

    titulo = QLabel("Gerenciamento de Vendas")
    titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    layout.addWidget(titulo)

    self.tabela = QTableWidget()
    self.tabela.setColumnCount(4)
    self.tabela.setHorizontalHeaderLabels(["ID", "Cliente", "Data", "Total"])
    layout.addWidget(self.tabela)

    btn_carregar = QPushButton("Atualizar Vendas Recentes")
    btn_carregar.clicked.connect(self.carregar_vendas)
    layout.addWidget(btn_carregar)

    btn_voltar = QPushButton("Voltar ao Menu Principal")
    btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(btn_voltar)

    self.setStyleSheet("background-color: #7b95a6; color: white;")
    self.carregar_vendas()

  def carregar_vendas(self):
    try:
      dados = (
          vw_vendas_recentes()
          if "vendas_recentes" in globals()
          else vw_vendas_recentes()
      )
      if dados:
        self.tabela.setRowCount(len(dados))
        for row_idx, row_data in enumerate(dados):
          for col_idx, valor in enumerate(row_data):
            self.tabela.setItem(
                row_idx, col_idx, QTableWidgetItem(str(valor))
            )
    except Exception as e:
      print(f"Erro ao carregar vendas: {e}")


# --- SUBMENU 2: ESTOQUE & PRODUTOS ---
class TelaEstoqueProdutos(QWidget):

  def __init__(self, sub_stack):
    super().__init__()
    self.sub_stack = sub_stack
    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)

    titulo = QLabel("Estoque e Alertas Críticos")
    titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    layout.addWidget(titulo)

    self.tabela_critico = QTableWidget()
    self.tabela_critico.setColumnCount(3)
    self.tabela_critico.setHorizontalHeaderLabels(
        ["Produto", "Qtd Atual", "Mínimo"]
    )
    layout.addWidget(
        QLabel("Produtos com Estoque Crítico (vw_estoque_critico):")
    )
    layout.addWidget(self.tabela_critico)

    btn_voltar = QPushButton("Voltar ao Menu Principal")
    btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(btn_voltar)

    self.setStyleSheet("background-color: #7b95a6; color: white;")
    self.carregar_estoque_critico()

  def carregar_estoque_critico(self):
    try:
      dados = vw_estoque_critico()
      if dados:
        self.tabela_critico.setRowCount(len(dados))
        for row_idx, row_data in enumerate(dados):
          for col_idx, valor in enumerate(row_data):
            self.tabela_critico.setItem(
                row_idx, col_idx, QTableWidgetItem(str(valor))
            )
    except Exception as e:
      print(f"Erro ao carregar estoque crítico: {e}")


# --- SUBMENU 3: CAIXA DIÁRIO ---
class TelaCaixaDiario(QWidget):

  def __init__(self, sub_stack):
    super().__init__()
    self.sub_stack = sub_stack
    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)

    titulo = QLabel("Resumo do Caixa Diário")
    titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    layout.addWidget(titulo)

    self.label_resumo = QLabel("Carregando resumo do caixa...")
    self.label_resumo.setFont(QFont("Arial", 14))
    layout.addWidget(self.label_resumo)

    btn_voltar = QPushButton("Voltar ao Menu Principal")
    btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(btn_voltar)

    self.setStyleSheet("background-color: #7b95a6; color: white;")
    self.carregar_caixa()

  def carregar_caixa(self):
    try:
      resumo = vw_resumo_caixa_diario()
      self.label_resumo.setText(f"Balanço / Resumo Atual:\n{resumo}")
    except Exception as e:
      self.label_resumo.setText(f"Erro ao buscar caixa diário: {e}")


# --- SUBMENU 4: CADASTROS & PONTOS ---
class TelaCadastrosPontos(QWidget):

  def __init__(self, sub_stack):
    super().__init__()
    self.sub_stack = sub_stack
    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)

    titulo = QLabel("Gerenciamento de Clientes & Pontos")
    titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    layout.addWidget(titulo)

    self.input_nome_cliente = QLineEdit()
    self.input_nome_cliente.setPlaceholderText("Nome do Cliente")
    layout.addWidget(self.input_nome_cliente)

    self.input_cpf_cliente = QLineEdit()
    self.input_cpf_cliente.setPlaceholderText("CPF do Cliente")
    layout.addWidget(self.input_cpf_cliente)

    btn_cad_cliente = QPushButton("Cadastrar Novo Cliente")
    btn_cad_cliente.clicked.connect(self.executar_cadastro_cliente)
    layout.addWidget(btn_cad_cliente)

    btn_voltar = QPushButton("Voltar ao Menu Principal")
    btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(btn_voltar)

    self.setStyleSheet("background-color: #7b95a6; color: white;")

  def executar_cadastro_cliente(self):
    nome = self.input_nome_cliente.text().strip()
    cpf = self.input_cpf_cliente.text().strip()
    if not nome or not cpf:
      QMessageBox.warning(self, "Aviso", "Preencha o nome e o CPF do cliente.")
      return
    try:
      cadastrar_cliente(nome=nome, cpf=cpf)
      QMessageBox.information(
          self, "Sucesso", "Cliente cadastrado com sucesso!"
      )
      self.input_nome_cliente.clear()
      self.input_cpf_cliente.clear()
    except Exception as e:
      QMessageBox.critical(self, "Erro", f"Erro ao cadastrar cliente: {e}")


# --- TELA DE PERFIL DO FUNCIONÁRIO LOGADO ---
class TelaPerfil(QWidget):

  def __init__(self, sub_stack, app_stack):
    super().__init__()
    self.sub_stack = sub_stack
    self.app_stack = app_stack
    layout = QVBoxLayout(self)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(20)

    titulo = QLabel("Perfil do Funcionário")
    titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
    layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)

    self.lbl_detalhes = QLabel("Nenhum usuário logado.")
    self.lbl_detalhes.setStyleSheet("font-size: 16px; color: #f0f0f0;")
    layout.addWidget(self.lbl_detalhes, alignment=Qt.AlignmentFlag.AlignHCenter)

    btn_logout = QPushButton("Terminar Sessão (Logout)")
    btn_logout.setFixedSize(220, 45)
    btn_logout.clicked.connect(self.fazer_logout)
    layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignHCenter)

    back_btn = QPushButton("Voltar ao Menu Principal")
    back_btn.setFixedSize(220, 45)
    back_btn.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    self.setStyleSheet("background-color: #7b95a6;")

  def carregar_dados_usuario(self):
    usuario = SessaoUsuario.obter_usuario()
    if usuario:
      self.lbl_detalhes.setText(
            f"Nome: {usuario.get('nome', 'Não informado')}\n"
            f"CPF: {usuario.get('cpf', 'Não informado')}\n"
            f"Telefone: {usuario.get('telefone', 'Não informado')}\n"
            f"E-mail: {usuario.get('email', 'Não informado')}"
      )
    else:
      self.lbl_detalhes.setText("Sessão ativa não encontrada.")
      self.fazer_logout

  def fazer_logout(self):
    SessaoUsuario.encerrar_sessao()
    QMessageBox.information(self, "Logout", "Sessão encerrada com sucesso.")
    self.app_stack.setCurrentIndex(1)


class TelaPrincipalSistema(QWidget):

  def __init__(self, parent=None, app_stack=None):
    super().__init__(parent)
    self.app_stack = app_stack
    self.init_ui()

  def init_ui(self):
    self.sub_stack = QStackedWidget(self)

    main_dashboard = QWidget()
    main_layout = QHBoxLayout(main_dashboard)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    # --- PAINEL ESQUERDO (Perfil + Botão de Estatísticas) ---
    esque_panel = QWidget()
    esque_layout = QVBoxLayout(esque_panel)
    esque_layout.setContentsMargins(10, 10, 10, 10)

    self.btn_perfil = QPushButton()
    self.btn_perfil.setFixedSize(120, 100)
    self.btn_perfil.setToolTip("Acessar Perfil")
    self.btn_perfil.clicked.connect(lambda: self.abrir_perfil())

    perfil_layout = QVBoxLayout(self.btn_perfil)
    lbl_perfil = QLabel("Perfil")
    lbl_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)
    perfil_layout.addWidget(lbl_perfil)

    # Botão para Acessar a Tela de Estatísticas
    btn_estatisticas = QPushButton("Estatísticas")
    btn_estatisticas.setMinimumHeight(40)
    # Direciona para o índice 6 (TelaEstatisticas)
    btn_estatisticas.clicked.connect(
        lambda: self.sub_stack.setCurrentIndex(6)
    )

    esque_layout.addWidget(btn_estatisticas)
    esque_layout.addStretch()
    esque_layout.addWidget(
        self.btn_perfil, alignment=Qt.AlignmentFlag.AlignHCenter
    )

    esque_panel.setFixedWidth(180)

    # --- PAINEL DIREITO (Grade 2x2 para os 4 Submenus) ---
    direi_panel = QWidget()
    direi_layout = QGridLayout(direi_panel)
    direi_layout.setContentsMargins(20, 20, 20, 20)
    direi_layout.setSpacing(15)

    nomes_submenus = [
        "Vendas\n(Vendas Recentes)",
        "Estoque & Produtos\n(Estoque Crítico)",
        "Caixa Diário\n(Resumo)",
        "Cadastros & Pontos\n(Clientes)",
    ]

    for index, nome in enumerate(nomes_submenus):
      linha = index // 2
      coluna = index % 2

      btn = QPushButton(nome)
      btn.setMinimumSize(140, 120)
      btn.setStyleSheet("font-size: 13px; font-weight: bold;")

      indice_destino = index + 2
      btn.clicked.connect(
          lambda checked, idx=indice_destino: self.sub_stack.setCurrentIndex(idx)
      )
      direi_layout.addWidget(btn, linha, coluna)

    main_layout.addWidget(esque_panel)
    main_layout.addWidget(direi_panel)

    # --- INSTANCIAÇÃO DAS PÁGINAS DO SUB_STACK ---
    self.perfil_page = TelaPerfil(self.sub_stack, self.app_stack)  # Índice 1
    self.vendas_page = TelaVendas(self.sub_stack)  # Índice 2
    self.estoque_page = TelaEstoqueProdutos(self.sub_stack)  # Índice 3
    self.caixa_page = TelaCaixaDiario(self.sub_stack)  # Índice 4
    self.cadastros_page = TelaCadastrosPontos(self.sub_stack)  # Índice 5
    self.estatisticas_page = TelaEstatisticas(self.sub_stack)  # Índice 6

    self.sub_stack.addWidget(main_dashboard)  # Índice 0
    self.sub_stack.addWidget(self.perfil_page)  # Índice 1
    self.sub_stack.addWidget(self.vendas_page)  # Índice 2
    self.sub_stack.addWidget(self.estoque_page)  # Índice 3
    self.sub_stack.addWidget(self.caixa_page)  # Índice 4
    self.sub_stack.addWidget(self.cadastros_page)  # Índice 5
    self.sub_stack.addWidget(self.estatisticas_page)  # Índice 6

    layout_global = QVBoxLayout(self)
    layout_global.setContentsMargins(0, 0, 0, 0)
    layout_global.addWidget(self.sub_stack)

  def atualizar_dados_perfil(self):
    self.perfil_page.carregar_dados_usuario()

  def abrir_perfil(self):
    self.atualizar_dados_perfil()
    self.sub_stack.setCurrentIndex(1)

class LojaCoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojaCore")
        self.setFixedSize(1337, 768)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.tela_cadastro = TelaCadastro(self.stack)
        self.tela_login = TelaLogin(self.stack)
        self.tela_principal = TelaPrincipalSistema(
            app_stack=self.stack
        )

        self.stack.addWidget(self.tela_cadastro)   # Índice 0
        self.stack.addWidget(self.tela_login)      # Índice 1
        self.stack.addWidget(self.tela_principal)  # Índice 2

        self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LojaCoreApp()
    window.show()

    sys.exit(app.exec())
