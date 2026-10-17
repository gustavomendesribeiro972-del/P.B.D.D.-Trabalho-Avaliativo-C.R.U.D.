import sys, re
from decimal import Decimal, InvalidOperation
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
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

#Restrições ao cadastrar:
def validar_nome_usuario(nome):
    nome = nome.strip()

    padrao = r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:\.[A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*$"

    return bool(re.fullmatch(padrao, nome))

def validar_email(email):
    email = email.strip().lower()

    padrao = (
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@(hotmail\.com|gmail\.com|email\.com)$"            
    )

    if not re.fullmatch(padrao, email):
        return False

    parte_local = email.split("@")[0]

    if(
        parte_local.startswith(".")
        or parte_local.endswith(".")
        or ".." in parte_local
    ): return False

    return True
#Eu era pra ter colocado junto com a classe de cadastro mas o programa não estava detectando as funções...

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

        if not validar_nome_usuario(nome):
            QMessageBox.warning(
                self,
                "Nome inválido",
                "O nome não pode conter espaços.\n"
                "Use pontos para separar as partes, "
                "por exemplo: joao.silva"
            )
            self.usuario.setFocus()
            return

        if not validar_email(email):
            QMessageBox.warning(
                self,
                "E-mail inválido",
                "Informe um e-mail válido terminado em "
                "@hotmail.com, @gmail.com ou @email.com."
            )
            self.email.setFocus()
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

        btn_atualizar = QPushButton("Atualizar Estatísticas")
        btn_atualizar.setMinimumHeight(40)
        btn_atualizar.clicked.connect(self.carregar_dados_estatisticas)

        btn_voltar = QPushButton("⬅ Voltar ao Menu Principal")
        btn_voltar.setMinimumHeight(40)
        btn_voltar.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))

        botoes_layout.addWidget(btn_atualizar)
        botoes_layout.addWidget(btn_voltar)

        layout.addLayout(botoes_layout)

        # Carrega as estatísticas ao inicializar
        self.carregar_dados_estatisticas()

    def criar_card(self, titulo, valor_inicial):
        """Cria um card visual estilizado para exibir métricas."""
        frame = QFrame()
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
        # 1. Vendas recentes
        try:
            dados_vendas = vw_vendas_recentes() or []
            self.atualizar_valor_card(
                self.card_vendas,
                len(dados_vendas)
            )
        except Exception as e:
            self.atualizar_valor_card(self.card_vendas, "Erro")
            print(f"Erro ao carregar vendas: {e}")

        # 2. Resumo do caixa
        try:
            resumo = vw_resumo_caixa_diario()
            self.atualizar_valor_card(
                self.card_caixa,
                str(resumo) if resumo is not None else "R$ 0,00"
            )
        except Exception as e:
            self.atualizar_valor_card(self.card_caixa, "Erro")
            print(f"Erro ao carregar caixa: {e}")

        # 3. Estoque crítico
        try:
            dados_criticos = vw_estoque_critico() or []
            self.atualizar_valor_card(
                self.card_estoque,
                len(dados_criticos)
            )
        except Exception as e:
            self.atualizar_valor_card(self.card_estoque, "Erro")
            print(f"Erro ao carregar estoque crítico: {e}")

        # 4. Tabela geral do estoque
        self.tabela_geral.setRowCount(0)

        try:
            dados_gerais = vw_geral_estoque_produtos() or []

            self.tabela_geral.setRowCount(len(dados_gerais))

            for linha, registro in enumerate(dados_gerais):
                for coluna, valor in enumerate(registro):
                    if coluna < self.tabela_geral.columnCount():
                        self.tabela_geral.setItem(
                            linha,
                            coluna,
                            QTableWidgetItem(str(valor))
                        )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro nas estatísticas",
                f"Não foi possível carregar o estoque:\n{e}"
            )


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

    self.carregar_vendas()

  def carregar_vendas(self):
    self.tabela.setRowCount(0)

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


class TelaEstoqueProdutos(QWidget):

    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Estoque e Alertas Críticos")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(titulo)

        layout.addWidget(
            QLabel("Produtos com Estoque Crítico:")
        )

        self.tabela_critico = QTableWidget()
        self.tabela_critico.setColumnCount(3)
        self.tabela_critico.setHorizontalHeaderLabels(
            ["Produto", "Qtd Atual", "Mínimo"]
        )
        self.tabela_critico.setAlternatingRowColors(True)
        layout.addWidget(self.tabela_critico)

        btn_atualizar = QPushButton("Atualizar Estoque")
        btn_atualizar.clicked.connect(
            self.carregar_estoque_critico
        )
        layout.addWidget(btn_atualizar)

        btn_voltar = QPushButton("Voltar ao Menu Principal")
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )
        layout.addWidget(btn_voltar)

        self.carregar_estoque_critico()

    def carregar_estoque_critico(self):
        self.tabela_critico.setRowCount(0)

        try:
            dados = vw_estoque_critico() or []

            self.tabela_critico.setRowCount(len(dados))

            for linha, registro in enumerate(dados):
                for coluna, valor in enumerate(registro):
                    self.tabela_critico.setItem(
                        linha,
                        coluna,
                        QTableWidgetItem(str(valor))
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao carregar estoque",
                str(e)
            )


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

    self.carregar_caixa()

  def carregar_caixa(self):
    try:
      resumo = vw_resumo_caixa_diario()
      self.label_resumo.setText(f"Balanço / Resumo Atual:\n{resumo}")
    except Exception as e:
      self.label_resumo.setText(f"Erro ao buscar caixa diário: {e}")


class TelaCadastrosPontos(QWidget):

    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        # Layout principal da página
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(12)

        # Área superior: botão de voltar à esquerda
        layout_topo = QHBoxLayout()

        btn_voltar = QPushButton("← Menu Principal")
        btn_voltar.setFixedSize(145, 35)
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )

        layout_topo.addWidget(
            btn_voltar,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        layout_topo.addStretch()

        layout_principal.addLayout(layout_topo)

        # Centralização vertical e horizontal do conteúdo
        layout_principal.addStretch()

        layout_central = QVBoxLayout()
        layout_central.setAlignment(
            Qt.AlignmentFlag.AlignHCenter
        )

        # Contêiner semelhante às telas de Cadastro e Login
        self.frame = QFrame()
        self.frame.setObjectName("cadastroCliente")
        self.frame.setFixedWidth(500)

        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(30, 25, 30, 25)
        frame_layout.setSpacing(15)

        # Título
        titulo = QLabel("Cadastro de Clientes")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)

        descricao = QLabel(
            "Preencha os dados para cadastrar um novo cliente."
        )
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(descricao)

        # Campo Nome
        self.input_nome_cliente = QLineEdit()
        self.input_nome_cliente.setPlaceholderText("Nome completo")
        self.input_nome_cliente.setMinimumHeight(42)
        frame_layout.addWidget(self.input_nome_cliente)

        # Campo CPF
        self.input_cpf_cliente = QLineEdit()
        self.input_cpf_cliente.setPlaceholderText("CPF")
        self.input_cpf_cliente.setMinimumHeight(42)
        frame_layout.addWidget(self.input_cpf_cliente)

        # Campo Email
        self.input_email_cliente = QLineEdit()
        self.input_email_cliente.setPlaceholderText("CPF")
        self.input_email_cliente.setMinimumHeight(42)
        frame_layout.addWidget(self.input_email_cliente)

        layout_central.addWidget(self.frame)
        layout_principal.addLayout(layout_central)

        # Botão abaixo do contêiner
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()

        btn_cad_cliente = QPushButton("Novo Cliente")
        btn_cad_cliente.setFixedSize(130, 35)
        btn_cad_cliente.clicked.connect(
            self.executar_cadastro_cliente
        )

        layout_botoes.addWidget(btn_cad_cliente)
        layout_botoes.addStretch()

        layout_principal.addLayout(layout_botoes)
        layout_principal.addStretch()

    def executar_cadastro_cliente(self):
        nome = self.input_nome_cliente.text().strip()
        cpf = self.input_cpf_cliente.text().strip()
        email = self.input_email_cliente.text().strip()

        if not nome or not cpf:
            QMessageBox.warning(
                self,
                "Atenção",
                "Preencha o nome e o CPF do cliente."
            )
            return

        try:
            cadastrar_cliente(nome=nome, cpf=cpf, email=email)

            QMessageBox.information(
                self,
                "Sucesso",
                "Cliente cadastrado com sucesso!"
            )

            self.input_nome_cliente.clear()
            self.input_cpf_cliente.clear()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao cadastrar cliente:\n{e}"
            )


class TelaPerfil(QWidget):

  def __init__(self, sub_stack, app_stack):
    super().__init__()
    self.sub_stack = sub_stack
    self.app_stack = app_stack
    layout = QVBoxLayout(self)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(20)

    titulo = QLabel("Perfil do Funcionário")
    layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignHCenter)

    self.lbl_detalhes = QLabel("Nenhum usuário logado.")
    layout.addWidget(self.lbl_detalhes, alignment=Qt.AlignmentFlag.AlignHCenter)

    btn_logout = QPushButton("Terminar Sessão (Logout)")
    btn_logout.setFixedSize(220, 45)
    btn_logout.clicked.connect(self.fazer_logout)
    layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignHCenter)

    back_btn = QPushButton("Voltar ao Menu Principal")
    back_btn.setFixedSize(220, 45)
    back_btn.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)


  def carregar_dados_usuario(self):
    usuario = SessaoUsuario.obter_usuario()

    if not usuario:
        self.lbl_detalhes.setText("Nenhum usuário logado.")
        return

    self.lbl_detalhes.setText(
        f"Nome: {usuario.get('nome_Usuario', 'Não informado')}\n"
        f"CPF: {usuario.get('cpf', 'Não informado')}\n"
        f"Telefone: {usuario.get('telefone', 'Não informado')}\n"
        f"E-mail: {usuario.get('email', 'Não informado')}"
    )

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

        # ===== MENU PRINCIPAL =====
        main_dashboard = QWidget()
        main_layout = QHBoxLayout(main_dashboard)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ===== PAINEL LATERAL =====
        painel = QFrame()
        painel.setObjectName("painelLateral")
        painel.setFixedWidth(210)

        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(12, 16, 12, 16)
        painel_layout.setSpacing(12)

        # Espaço para o ícone/logotipo.
        self.lbl_icone = QLabel()
        self.lbl_icone.setObjectName("iconeLoja")
        self.lbl_icone.setFixedSize(120, 100)
        self.lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Coloque icon.jpeg na pasta do programa.
        pixmap = QIcon("icon.jpeg").pixmap(90, 90)

        if not pixmap.isNull():
            self.lbl_icone.setPixmap(pixmap)
        else:
            self.lbl_icone.setText("LojaCore")

        painel_layout.addWidget(
            self.lbl_icone,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        nome_loja = QLabel("LojaCore")
        nome_loja.setObjectName("nomeLoja")
        nome_loja.setAlignment(Qt.AlignmentFlag.AlignCenter)
        painel_layout.addWidget(nome_loja)

        painel_layout.addSpacing(12)

        self.btn_perfil = QPushButton("  Perfil")
        self.btn_perfil.setMinimumHeight(42)
        self.btn_perfil.clicked.connect(self.abrir_perfil)
        painel_layout.addWidget(self.btn_perfil)

        btn_estatisticas = QPushButton("  Estatísticas")
        btn_estatisticas.setMinimumHeight(42)
        btn_estatisticas.clicked.connect(
            lambda: self.abrir_pagina("estatisticas")
        )
        painel_layout.addWidget(btn_estatisticas)

        btn_conexao = QPushButton("  Testar conexão")
        btn_conexao.setMinimumHeight(42)
        btn_conexao.clicked.connect(self.testar_conexao)
        painel_layout.addWidget(btn_conexao)

        painel_layout.addStretch()

        # ===== ÁREA DE CONTEÚDO =====
        conteudo = QWidget()
        conteudo_layout = QVBoxLayout(conteudo)
        conteudo_layout.setContentsMargins(0, 0, 0, 0)
        conteudo_layout.setSpacing(12)

        titulo = QLabel("Painel Principal")
        titulo.setObjectName("tituloPagina")
        conteudo_layout.addWidget(titulo)

        subtitulo = QLabel(
            "Selecione uma das opções para continuar."
        )
        subtitulo.setObjectName("subtitulo")
        conteudo_layout.addWidget(subtitulo)

        grade = QGridLayout()
        grade.setSpacing(16)

        opcoes = [
            ("Vendas Recentes", "Consultar as vendas", "vendas"),
            ("Estoque e Produtos", "Consultar estoque crítico", "estoque"),
            ("Caixa Diário", "Ver resumo do caixa", "caixa"),
            ("Clientes e Pontos", "Gerenciar clientes", "cadastros"),
            ("Registrar Venda", "Lançar uma nova venda", "registrar_venda"),
            ("Status do Produto", "Consultar um produto", "status_produto"),
            ("Calcular Pontos", "Calcular pontos da compra", "pontos"),
            ("Estatísticas", "Indicadores do sistema", "estatisticas"),
        ]

        for i, (nome, descricao, chave) in enumerate(opcoes):
            card = QFrame()
            card.setObjectName("cardMenu")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(8)

            lbl_nome = QLabel(nome)
            lbl_nome.setObjectName("tituloCard")

            lbl_descricao = QLabel(descricao)
            lbl_descricao.setObjectName("descricaoCard")
            lbl_descricao.setWordWrap(True)

            btn = QPushButton("Abrir página")
            btn.setMinimumHeight(38)
            btn.clicked.connect(
                lambda checked=False, k=chave: self.abrir_pagina(k)
            )

            card_layout.addWidget(lbl_nome)
            card_layout.addWidget(lbl_descricao)
            card_layout.addStretch()
            card_layout.addWidget(btn)

            grade.addWidget(card, i // 2, i % 2)

        conteudo_layout.addLayout(grade)
        conteudo_layout.addStretch()

        main_layout.addWidget(painel)
        main_layout.addWidget(conteudo, 1)

        # ===== INSTANCIAR AS PÁGINAS =====
        self.paginas = {}

        def adicionar_pagina(chave, widget):
            self.paginas[chave] = widget
            self.sub_stack.addWidget(widget)

        adicionar_pagina("inicio", main_dashboard)
        adicionar_pagina(
            "perfil", TelaPerfil(self.sub_stack, self.app_stack)
        )
        adicionar_pagina("vendas", TelaVendas(self.sub_stack))
        adicionar_pagina(
            "estoque", TelaEstoqueProdutos(self.sub_stack)
        )
        adicionar_pagina("caixa", TelaCaixaDiario(self.sub_stack))
        adicionar_pagina(
            "cadastros", TelaCadastrosPontos(self.sub_stack)
        )
        adicionar_pagina(
            "estatisticas", TelaEstatisticas(self.sub_stack)
        )
        adicionar_pagina(
            "registrar_venda", TelaRegistrarVenda(self.sub_stack)
        )
        adicionar_pagina(
            "status_produto", TelaStatusProduto(self.sub_stack)
        )
        adicionar_pagina(
            "pontos", TelaCalcularPontos(self.sub_stack)
        )

        layout_global = QVBoxLayout(self)
        layout_global.setContentsMargins(0, 0, 0, 0)
        layout_global.addWidget(self.sub_stack)

        self.sub_stack.setCurrentWidget(main_dashboard)

    def abrir_pagina(self, chave):
        pagina = self.paginas.get(chave)

        if pagina is not None:
            self.sub_stack.setCurrentWidget(pagina)


    def atualizar_dados_perfil(self):
        self.paginas["perfil"].carregar_dados_usuario()


    def abrir_perfil(self):
        self.atualizar_dados_perfil()
        self.abrir_pagina("perfil")


    def testar_conexao(self):
        try:
            resultado = testar_conexao()

            if resultado is False or resultado is None:
                QMessageBox.warning(
                    self,
                    "Teste de conexão",
                    f"A função retornou: {resultado}\n"
                    "Verifique a implementação de testar_conexao "
                    "em conexao.py."
                )
            else:
                QMessageBox.information(
                    self,
                    "Teste de conexão",
                    f"Resultado: {resultado}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Falha na conexão",
                f"Não foi possível testar a conexão:\n{e}"
            )


class TelaRegistrarVenda(QWidget):

    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        principal = QVBoxLayout(self)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(12)

        topo = QHBoxLayout()
        btn_voltar = QPushButton("← Menu Principal")
        btn_voltar.setFixedSize(145, 35)
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )
        topo.addWidget(btn_voltar)
        topo.addStretch()
        principal.addLayout(topo)

        principal.addStretch()

        self.frame = QFrame()
        self.frame.setObjectName("cadastroCliente")
        self.frame.setFixedWidth(500)

        formulario = QVBoxLayout(self.frame)
        formulario.setContentsMargins(30, 25, 30, 25)
        formulario.setSpacing(15)

        titulo = QLabel("Registrar Venda")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulario.addWidget(titulo)

        descricao = QLabel(
            "Preencha os dados para registrar uma venda."
        )
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formulario.addWidget(descricao)

        self.cliente_id = QLineEdit()
        self.cliente_id.setPlaceholderText("ID do cliente")
        self.cliente_id.setMinimumHeight(42)
        formulario.addWidget(self.cliente_id)

        self.produto_id = QLineEdit()
        self.produto_id.setPlaceholderText("ID do produto")
        self.produto_id.setMinimumHeight(42)
        formulario.addWidget(self.produto_id)

        self.quantidade = QLineEdit()
        self.quantidade.setPlaceholderText("Quantidade")
        self.quantidade.setMinimumHeight(42)
        formulario.addWidget(self.quantidade)

        principal.addWidget(
            self.frame,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_registrar = QPushButton("Registrar Venda")
        btn_registrar.setFixedSize(145, 35)
        btn_registrar.clicked.connect(self.registrar)
        botoes.addWidget(btn_registrar)

        botoes.addStretch()
        principal.addLayout(botoes)
        principal.addStretch()

    def registrar(self):
        cliente = self.cliente_id.text().strip()
        produto = self.produto_id.text().strip()
        quantidade = self.quantidade.text().strip()

        if not cliente or not produto or not quantidade:
            QMessageBox.warning(
                self, "Atenção",
                "Preencha todos os campos."
            )
            return

        try:
            cliente_id = int(cliente)
            produto_id = int(produto)
            qtd = int(quantidade)

            if cliente_id <= 0 or produto_id <= 0 or qtd <= 0:
                raise ValueError(
                    "Os IDs e a quantidade devem ser positivos."
                )

            # Confirme a assinatura em conexao.py.
            resultado = registrar_venda(
                cliente_id, produto_id, qtd
            )

            if resultado is False:
                QMessageBox.warning(
                    self, "Venda",
                    "Não foi possível registrar a venda."
                )
                return

            QMessageBox.information(
                self, "Venda",
                "Solicitação de registro concluída."
            )

            self.cliente_id.clear()
            self.produto_id.clear()
            self.quantidade.clear()

        except ValueError as e:
            QMessageBox.warning(
                self, "Dados inválidos", str(e)
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erro ao registrar venda", str(e)
            )


class TelaStatusProduto(QWidget):
    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        titulo = QLabel("Status do Produto")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        self.produto_id = QLineEdit()
        self.produto_id.setPlaceholderText("ID do produto")
        layout.addWidget(self.produto_id)

        btn_consultar = QPushButton("Consultar Status")
        btn_consultar.clicked.connect(self.consultar)
        layout.addWidget(btn_consultar)

        self.resultado = QLabel("Informe o ID do produto.")
        self.resultado.setWordWrap(True)
        layout.addWidget(self.resultado)

        btn_voltar = QPushButton("Voltar ao Menu")
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )
        layout.addWidget(btn_voltar)

        layout.addStretch()

    def consultar(self):
        texto = self.produto_id.text().strip()

        if not texto:
            QMessageBox.warning(
                self, 
                "Atenção",
                "Informe o ID do produto."
            )
            return

        try:
            produto_id = int(texto)

            if produto_id <= 0:
                raise ValueError("O ID deve ser positivo.")

            # Ajuste conforme a assinatura real da função.
            status = fn_status_produto(produto_id)

            if status is None or status is False:
                self.resultado.setText("Este produto não existe...")

            elif isinstance(status, str) and not status.strip():
                self.resultado.setText("Este produto não existe...")

            else:
                self.resultado.setText(
                    f"Status do produto {produto_id}:\n{status}"
                )

        except ValueError as e:
            QMessageBox.warning(
                self, "ID inválido", str(e)
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Erro ao consultar produto", str(e)
            )


class TelaCalcularPontos(QWidget):
    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        titulo = QLabel("Calcular Pontos da Compra")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Digite o valor total da compra em reais."
        )
        layout.addWidget(descricao)

        self.valor_compra = QLineEdit()
        self.valor_compra.setPlaceholderText("Ex.: 150,00")
        layout.addWidget(self.valor_compra)

        btn_calcular = QPushButton("Calcular Pontos")
        btn_calcular.clicked.connect(self.calcular)
        layout.addWidget(btn_calcular)

        self.resultado = QLabel("")
        self.resultado.setWordWrap(True)
        layout.addWidget(self.resultado)

        btn_voltar = QPushButton("Voltar ao Menu")
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )
        layout.addWidget(btn_voltar)

        layout.addStretch()

    def calcular(self):
        texto = self.valor_compra.text().strip()
        texto = texto.replace("R$", "").replace(" ", "")

        if not texto:
            QMessageBox.warning(
                self, "Atenção",
                "Informe o valor da compra."
            )
            return

        try:
            # Aceita valores como 150,00 ou 150.00.
            if "," in texto and "." in texto:
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", ".")

            valor = Decimal(texto)

            if not valor.is_finite() or valor <= 0:
                raise ValueError(
                    "O valor deve ser maior que zero."
                )

            # Ajuste conforme a assinatura real da função.
            pontos = fn_calcular_pontos_compra(float(valor))

            self.resultado.setText(
                f"Valor da compra: R$ {valor:.2f}\n"
                f"Pontos calculados: {pontos}"
            )

        except (ValueError, ArithmeticError) as e:
            QMessageBox.warning(
                self, "Valor inválido", str(e)
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Erro ao calcular pontos", str(e)
            )



class LojaCoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojaCore")
        self.setWindowIcon(QIcon("icon.jpeg"))
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

        self.aplicar_estilo()

        self.stack.setCurrentIndex(0)

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F6FA;
                color: #243447;
                font-family: Arial;
                font-size: 13px;
            }

            #painelLateral {
                background-color: #172B3A;
                border-radius: 12px;
            }

            #painelLateral QLabel {
                background-color: transparent;
                color: white;
            }

            #nomeLoja {
                font-size: 21px;
                font-weight: bold;
            }

            #iconeLoja {
                background-color: #29495D;
                border: 1px solid #496170;
                border-radius: 12px;
            }

            #painelLateral QPushButton {
                background-color: #29495D;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px;
                text-align: left;
            }

            #painelLateral QPushButton:hover {
                background-color: #3B6279;
            }

            #tituloPagina {
                font-size: 23px;
                font-weight: bold;
                color: #172B3A;
                padding: 5px;
            }

            #subtitulo {
                color: #64748B;
                font-size: 14px;
            }

            #cardMenu {
                background-color: white;
                border: 1px solid #E0E7EF;
                border-radius: 12px;
            }

            #tituloCard {
                background-color: transparent;
                color: #172B3A;
                font-size: 15px;
                font-weight: bold;
            }

            #descricaoCard {
                background-color: transparent;
                color: #64748B;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 10px;
                min-height: 20px;
            }

            QLineEdit:focus {
                border: 1px solid #3478A5;
            }

            QPushButton {
                background-color: #246B8E;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #195571;
            }

            QTableWidget {
                background-color: white;
                alternate-background-color: #F1F5F9;
                border: 1px solid #DCE4EC;
                border-radius: 7px;
                gridline-color: #E2E8F0;
            }

            QHeaderView::section {
                background-color: #29495D;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            #cadastroCliente {
                background-color: white;
                border: 1px solid #DCE4EC;
                border-radius: 12px;
            }

            #cadastroCliente QLabel {
                background-color: transparent;
            }

            #cadastroCliente QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 10px;
            }

            #cadastroCliente QLineEdit:focus {
                border: 1px solid #3478A5;
            }
        """)


if __name__ == "__main__":
    import platform

    if platform.system() == "Windows":
        import ctypes
        myappid = "unifsa.lojacore.v.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = LojaCoreApp()
    window.show()

    sys.exit(app.exec())