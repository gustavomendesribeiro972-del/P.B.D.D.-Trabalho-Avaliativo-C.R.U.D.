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

# Importa as todas as funções(Views, Functions e Procedures) do conexao:
from conexao import (
    vw_vendas_recentes, #Presente na pagina vendas
    vw_geral_estoque_produtos, #Presente na pagina vendas
    vw_estoque_critico, #Presente na pagina vendas
    vw_resumo_caixa_diario, #Presente na pagina vendas

    fn_autenticar_funcionario, #Presente na pagina de cadastro / login
    fn_status_produto, #Presente na pagina de produto
    fn_calcular_pontos_compra, #Presente na pagina cliente

    cadastrar_cliente,  #Presente na pagina de cadastro / login
    registrar_funcionarios, #Presente na pagina de cadastro / login
    registrar_venda, #Presente na pagina vendas
    testar_conexao, #presente na pagina main, venda e cadastro / login
)



class TelaCadastro(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #Layout da Janela:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        frame = QFrame()
        frame.setFixedSize(657, 588)
        frame.setObjectName("cadastro")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 18, 25, 20)
        frame_layout.setSpacing(15)

        #Os Widgets:
        titulo = QLabel("Cadastro")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuário")
        self.usuario.setMinimumHeight(45)

        self.apelido = QLineEdit()
        self.apelido.setPlaceholderText("Apelido")

        self.cpf = QLineEdit()
        self.cpf.setPlaceholderText("CPF")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-mail")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.EchoMode.Password)

        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.setMinimumHeight(45)
        botao_cadastrar.clicked.connect(self.ir_para_login)

        botao_ir_login = QPushButton("Já tenho conta")
        botao_ir_login.clicked.connect(self.ir_para_login)
        
        #Loop, para cada widget em (os widgets), adicionar-los no frame_layout(frame), assim concluido adicionar o frame em layout.
        for widget in (
            titulo, self.usuario, self.apelido, self.cpf,
            self.email, self.senha, botao_cadastrar, botao_ir_login
        ):
            frame_layout.addWidget(widget)

        layout.addWidget(frame)

    #ações:
    def realizar_cadastro(self):
       #AQUI A FUNÇÃO registrar_funcionario
       self.parent().setCurrentIndex(1)

    def ir_para_login(self):
        # parent é o QStackedWidget
        self.parent().setCurrentIndex(1)


class TelaLogin(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #Layout da janela:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        frame = QFrame()
        frame.setFixedSize(657, 588)
        frame.setObjectName("login")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 18, 25, 20)
        frame_layout.setSpacing(15)

        #Os widgets:
        titulo = QLabel("Login")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuário")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.EchoMode.Password)

        botao_entrar = QPushButton("Entrar")
        botao_entrar.setMinimumHeight(45)
        botao_entrar.clicked.connect(self.realizar_login)

        #Loop, para cada widget em (os widgets), adicionar-los no frame_layout(frame), assim concluido adicionar o frame em layout.
        for widget in (titulo, self.usuario, self.senha, botao_entrar):
            frame_layout.addWidget(widget)
        layout.addWidget(frame)

    #ações:
    def realizar_login(self):
        #AQUI A FUNÇÃO fn_authenticar_usuario
        self.parent().setCurrentIndex(2)

    def ir_para_cadastro(self):
        self.parent().setCurrentIndex(0)

class TelaEstatisticas(QWidget):
    def __init__(self, parent=None):
        #Layout da Janela:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        frame = QFrame()
        frame.setFixedSize(682, 638)
        frame.setObjectName("Estatisticas")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 18, 25, 20)
        frame_layout.setSpacing(15)

        #Os Widgets:
        label_estatisticas = QLabel("Painel")
        label_estatisticas.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        frame_layout.addWidget(label_estatisticas)

        layout.addWidget(frame)

        #OBS: CONTINUAR

class TelaPrincipalSistema(QWidget):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.init_ui()

  def init_ui(self):
    # QStackedWidget interno para gerenciar a troca entre o Dashboard Principal e as páginas internas (como Perfil ou Submenus)
    self.sub_stack = QStackedWidget(self)

    # Criação da página principal dividida em dois painéis
    main_dashboard = QWidget()
    main_layout = QHBoxLayout(main_dashboard)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    # --- PAINEL ESQUERDO (Perfil) ---
    esque_panel = QWidget()
    esque_layout = QVBoxLayout(esque_panel)
    esque_layout.setContentsMargins(10, 10, 10, 10)

    nomes_submenus = [
       "Vendas",
       "Clientes",
       "Estoque",
       "Caixa Diário",
       "Produtos",
       "Funcionários",
       "Pontos",
       "Configurações"
    ]

    self.btn_perfil = QPushButton()
    self.btn_perfil.setFixedSize(120, 80)
    self.btn_perfil.setToolTip("Acessar Perfil")
    self.btn_perfil.clicked.connect(lambda: self.sub_stack.setCurrentIndex(1))

    perfil_layout = QVBoxLayout(self.btn_perfil)
    lbl_perfil = QLabel("👤 Perfil")
    lbl_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)
    perfil_layout.addWidget(lbl_perfil)

    esque_layout.addStretch()
    esque_layout.addWidget(
        self.btn_perfil, alignment=Qt.AlignmentFlag.AlignHCenter
    )

    esque_panel.setFixedWidth(180)

    # --- PAINEL DIREITO (Grade 3x3 de Submenus) ---
    direi_panel = QWidget()
    direi_layout = QGridLayout(direi_panel)
    direi_layout.setContentsMargins(20, 20, 20, 20)
    direi_layout.setSpacing(15)

    positions = [(i, j) for i in range(3) for j in range(3)]
    for index, pos in enumerate(positions):
      textos_botoes = (
         nomes_submenus[index]
         if index < len(nomes_submenus)
         else f"Submenu {index + 1}"
      )
      btn = QPushButton(textos_botoes)
      btn.setMinimumSize(100, 100)
      btn.clicked.connect(lambda checked, idx=index + 1: self.abrir_submenu(idx))
      direi_layout.addWidget(btn, pos[0], pos[1])

    main_layout.addWidget(esque_panel)
    main_layout.addWidget(direi_panel)

    # Páginas de detalhes internas
    self.perfil_page = self.criar_pagina_detalhe(
        "Página de Perfil", "Gerencie suas informações de usuário aqui."
    )
    self.submenu_page = self.criar_pagina_detalhe(
        "Submenu", "Conteúdo correspondente à opção selecionada."
    )

    # Adiciona as páginas ao sub_stack interno
    self.sub_stack.addWidget(main_dashboard)  # Índice 0 (Tela Dupla)
    self.sub_stack.addWidget(self.perfil_page)  # Índice 1 (Perfil)
    self.sub_stack.addWidget(self.submenu_page)  # Índice 2 (Submenus)

    # Layout global desta classe
    layout_global = QVBoxLayout(self)
    layout_global.setContentsMargins(0, 0, 0, 0)
    layout_global.addWidget(self.sub_stack)

  def criar_pagina_detalhe(self, titulo_texto, desc_texto):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(20)

    title = QLabel(titulo_texto)
    title.setStyleSheet("font-size: 24px; font-weight: bold;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    description = QLabel(desc_texto)
    description.setStyleSheet("font-size: 16px; color: #f0f0f0;")
    description.setAlignment(Qt.AlignmentFlag.AlignCenter)

    back_btn = QPushButton("Voltar ao Menu Principal")
    back_btn.setFixedSize(200, 40)
    back_btn.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))

    layout.addWidget(title)
    layout.addWidget(description)
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    return page

  def abrir_submenu(self, index):
    # Atualiza dinamicamente o texto da página de submenu com base no botão clicado
    self.submenu_page.layout().itemAt(0).widget().setText(f"Submenu {index}")
    self.submenu_page.layout().itemAt(1).widget().setText(
        f"Você acessou o conteúdo detalhado referente ao Submenu {index}."
    )
    self.sub_stack.setCurrentIndex(2)

class LojaCoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojaCore")
        self.resize(1167, 718)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.tela_cadastro = TelaCadastro()
        self.tela_login = TelaLogin()
        self.tela_principal = TelaPrincipalSistema()

        self.stack.addWidget(self.tela_cadastro)  # índice 0
        self.stack.addWidget(self.tela_login)     # índice 1
        self.stack.addWidget(self.tela_principal) # Indice 2

        self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LojaCoreApp()
    window.show()

    sys.exit(app.exec())
