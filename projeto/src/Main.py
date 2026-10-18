import sys, re
from decimal import Decimal, InvalidOperation
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QStackedWidget,
    QLabel,
    QPlainTextEdit,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
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

    app_buscar_funcionario_por_cpf,  #Presente na página de Login / Perfil
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

def formatar_moeda(valor):
    """Formata um valor numérico como moeda brasileira."""
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite():
            return str(valor)

        formatado = f"{numero:,.2f}"
        formatado = formatado.replace(",", "X")
        formatado = formatado.replace(".", ",")
        formatado = formatado.replace("X", ".")
        return f"R$ {formatado}"

    except (InvalidOperation, ValueError, TypeError):
        return str(valor)


def formatar_resumo_caixa(resumo):
    """Formata os dados do caixa para exibição na interface."""

    if resumo is None:
        return "Nenhum movimento registrado."

    # Converte um registro Row do SQLAlchemy em dicionário.
    if hasattr(resumo, "_mapping"):
        resumo = dict(resumo._mapping)

    # Trata um único registro representado por dicionário.
    if isinstance(resumo, dict):
        if not resumo:
            return "Nenhum movimento registrado."

        linhas = ["RESUMO DO CAIXA DIÁRIO", ""]

        for chave, valor in resumo.items():
            nome = str(chave).replace("_", " ").capitalize()

            if valor is None:
                valor_formatado = "Não informado"

            elif isinstance(valor, (int, float, Decimal)):
                chave_normalizada = str(chave).lower()

                termos_monetarios = (
                    "valor", "total", "saldo", "receita",
                    "faturamento", "caixa", "venda",
                    "desconto", "entrada", "saida",
                    "saída", "lucro", "dinheiro"
                )

                if any(
                    termo in chave_normalizada
                    for termo in termos_monetarios
                ):
                    valor_formatado = formatar_moeda(valor)
                else:
                    valor_formatado = str(valor)

            else:
                valor_formatado = str(valor)

            linhas.append(f"{nome}: {valor_formatado}")

        return "\n".join(linhas)

    # Trata a lista de registros retornada por fetchall().
    if isinstance(resumo, (list, tuple)):
        if not resumo:
            return "Nenhum movimento registrado."

        if len(resumo) == 1:
            return formatar_resumo_caixa(resumo[0])

        linhas = ["RESUMO DO CAIXA DIÁRIO", ""]

        for indice, registro in enumerate(resumo, start=1):
            linhas.append(f"Registro {indice}:")

            if hasattr(registro, "_mapping"):
                registro = dict(registro._mapping)

            if isinstance(registro, dict):
                texto_registro = formatar_resumo_caixa(registro)
                # Evita repetir o título principal em cada registro.
                texto_registro = texto_registro.replace(
                    "RESUMO DO CAIXA DIÁRIO\n\n", "", 1
                )
                linhas.append(texto_registro)

            elif isinstance(registro, (list, tuple)):
                linhas.extend(
                    f"Campo {i}: {valor}"
                    for i, valor in enumerate(registro, start=1)
                )

            else:
                linhas.append(str(registro))

            linhas.append("")

        return "\n".join(linhas).strip()

    if isinstance(resumo, (int, float, Decimal)):
        return (
            "RESUMO DO CAIXA DIÁRIO\n\n"
            f"Saldo/Total: {formatar_moeda(resumo)}"
        )

    return f"RESUMO DO CAIXA DIÁRIO\n\n{resumo}"


def formatar_resumo_caixa_card(resumo):
    """Retorna um indicador compacto para o card do caixa."""

    if resumo is None:
        return "Sem dados"

    # Aceita um registro SQLAlchemy.
    if hasattr(resumo, "_mapping"):
        resumo = dict(resumo._mapping)

    # Aceita uma lista de registros.
    if isinstance(resumo, (list, tuple)):
        if not resumo:
            return "Sem dados"

        if len(resumo) != 1:
            return "ver resumo diário..."

        return formatar_resumo_caixa_card(resumo[0])

    if not isinstance(resumo, dict):
        return "ver resumo diário..."

    # Prioriza campos que representam valores monetários.
    campos_prioritarios = (
        "saldo_caixa",
        "saldo",
        "total_caixa",
        "valor_caixa",
        "faturamento",
        "total_vendas",
        "valor_total",
        "total"
    )

    dados = {
        str(chave).lower(): valor
        for chave, valor in resumo.items()
    }

    for campo in campos_prioritarios:
        valor = dados.get(campo)

        if isinstance(valor, (int, float, Decimal)):
            if Decimal(str(valor)).is_finite():
                return formatar_moeda(valor)

    return "Ver resumo diário"


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

        if not nome or not cpf or not email or not senha:
            QMessageBox.warning(
                self,
                "Cadastro",
                "Preencha Nome, CPF, Email e Senha."
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

            self.stack.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(
                self,
                "SQLAlchemy",
                f"Não foi possível registrar: {e}"
            )

    def ir_para_login(self):
        self.stack.setCurrentIndex(0)


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
        self.stack.setCurrentIndex(1)


class TelaEstatisticas(QWidget):
    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título da Página
        titulo = QLabel("Painel de Estatísticas e Desempenho")
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
        self.tabela_geral.setColumnCount(10)
        self.tabela_geral.setHorizontalHeaderLabels([
            "ID Produto",
            "ID Variação",
            "Nome do Produto",
            "SKU",
            "ID Categoria",
            "Estoque Disponível",
            "Estoque Mínimo",
            "Status",
            "Custo Padrão",
            "Preço de Venda Base"
        ])
        self.tabela_geral.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabela_geral.horizontalHeader().setStretchLastSection(True)
        self.tabela_geral.setMinimumHeight(300)
        self.tabela_geral.setAlternatingRowColors(True)
        self.tabela_geral.setWordWrap(True)
        self.tabela_geral.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        layout.addWidget(self.tabela_geral)

        # Botões de Ação
        botoes_layout = QHBoxLayout()

        btn_atualizar = QPushButton("Atualizar Estatísticas")
        btn_atualizar.setMinimumHeight(40)
        btn_atualizar.clicked.connect(self.carregar_dados_estatisticas)

        btn_voltar = QPushButton("Voltar ao Menu Principal")
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
        lbl_valor.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_valor.setWordWrap(True)
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
                formatar_resumo_caixa_card(resumo)
            )

        except Exception as e:
            self.atualizar_valor_card(
                self.card_caixa,
                "Indisponível"
            )
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
                    if coluna >= self.tabela_geral.columnCount():
                        break

                    # Formata valores monetários.
                    if coluna in (8, 9) and valor is not None:
                        texto = formatar_moeda(valor)
                    elif valor is None:
                        texto = "—"
                    else:
                        texto = str(valor)

                    item = QTableWidgetItem(texto)

                    # Alinha valores numéricos à direita.
                    if coluna in (0, 1, 4, 5, 6, 8, 9):
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignRight
                            | Qt.AlignmentFlag.AlignVCenter
                        )

                    self.tabela_geral.setItem(linha, coluna, item)

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
    self.tabela.setColumnCount(8)
    self.tabela.setHorizontalHeaderLabels([
        "ID Venda",
        "Nº Cupom",
        "ID Cliente",
        "ID Funcionário",
        "Operador",
        "Total",
        "Status",
        "Data e Hora"
    ])

    self.tabela.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )
    self.tabela.horizontalHeader().setStretchLastSection(True)

    self.tabela.verticalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )

    self.tabela.setMinimumHeight(300)
    self.tabela.setAlternatingRowColors(True)
    self.tabela.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )

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
        dados = vw_vendas_recentes() or []

        self.tabela.setRowCount(len(dados))

        for linha, registro in enumerate(dados):
            for coluna, valor in enumerate(registro):
                if coluna >= self.tabela.columnCount():
                    break

                if coluna == 5 and valor is not None:
                    # Total da venda em reais.
                    texto = formatar_moeda(valor)

                elif coluna == 7 and valor is not None:
                    # Data e hora em formato legível.
                    if hasattr(valor, "strftime"):
                        texto = valor.strftime("%d/%m/%Y %H:%M:%S")
                    else:
                        texto = str(valor)

                elif valor is None:
                    texto = "—"

                else:
                    texto = str(valor)

                item = QTableWidgetItem(texto)

                if coluna in (0, 2, 3, 5):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    )

                self.tabela.setItem(linha, coluna, item)

    except Exception as e:
        QMessageBox.critical(
            self,
            "Erro ao carregar vendas",
            f"Não foi possível consultar as vendas recentes:\n{e}"
        )


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
        self.tabela_critico.setColumnCount(10)
        self.tabela_critico.setHorizontalHeaderLabels([
            "ID Produto",
            "Nome do Produto",
            "ID Variação",
            "SKU",
            "Tamanho",
            "Cor",
            "Código de Barras",
            "Estoque Atual",
            "Estoque Mínimo",
            "Necessidade de Reposição",
            " "
        ])

        self.tabela_critico.setAlternatingRowColors(True)

        self.tabela_critico.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabela_critico.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabela_critico.setMinimumHeight(300)

        self.tabela_critico.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.tabela_critico.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

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
                    if coluna < self.tabela_critico.columnCount():
                        item = QTableWidgetItem(
                            "" if valor is None else str(valor)
                        )
                        self.tabela_critico.setItem(linha, coluna, item)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao carregar estoque",
                f"Não foi possível carregar o estoque crítico:\n{e}"
            )


class TelaCaixaDiario(QWidget):

    def __init__(self, sub_stack):
        super().__init__()
        self.sub_stack = sub_stack

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("Resumo do Caixa Diário")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(titulo)

        self.texto_resumo = QPlainTextEdit()
        self.texto_resumo.setReadOnly(True)
        self.texto_resumo.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth
        )
        self.texto_resumo.setFont(QFont("Consolas", 11))
        self.texto_resumo.setPlainText(
            "Carregando resumo do caixa..."
        )
        layout.addWidget(self.texto_resumo)

        btn_atualizar = QPushButton("Atualizar Resumo")
        btn_atualizar.clicked.connect(self.carregar_caixa)
        layout.addWidget(btn_atualizar)

        btn_voltar = QPushButton("Voltar ao Menu Principal")
        btn_voltar.clicked.connect(
            lambda: self.sub_stack.setCurrentIndex(0)
        )
        layout.addWidget(btn_voltar)

        self.carregar_caixa()

    def carregar_caixa(self):
        try:
            dados = vw_resumo_caixa_diario() or []

            if not dados:
                self.texto_resumo.setPlainText(
                    "Nenhum movimento registrado no caixa diário."
                )
                return

            linhas = [
                "=" * 55,
                "             RESUMO DO CAIXA DIÁRIO",
                "=" * 55,
                ""
            ]

            for registro in dados:
                # Compatível com resultados do SQLAlchemy
                if hasattr(registro, "_mapping"):
                    registro = dict(registro._mapping)
                elif not isinstance(registro, dict):
                    registro = dict(registro)

                nome = registro.get(
                    "nome_operador", "Não informado"
                )
                funcionario = registro.get(
                    "id_funcionario", "Não informado"
                )
                data = registro.get(
                    "data_venda", "Não informada"
                )
                quantidade = registro.get(
                    "quantidade_vendas", 0
                )

                linhas.extend([
                    f"Operador: {nome}",
                    f"ID do funcionário: {funcionario}",
                    f"Data: {data}",
                    f"Quantidade de vendas: {quantidade}",
                    "",
                    f"Subtotal: {formatar_moeda(registro.get('total_subtotal', 0) or 0)}",
                    f"Descontos: {formatar_moeda(registro.get('total_descontos', 0) or 0)}",
                    f"Total faturado: {formatar_moeda(registro.get('total_faturado', 0) or 0)}",
                    f"Ticket médio: {formatar_moeda(registro.get('ticket_medio', 0) or 0)}",
                    "",
                    "-" * 55,
                    ""
                ])

            self.texto_resumo.setPlainText("\n".join(linhas))

        except Exception as e:
            self.texto_resumo.setPlainText(
                f"Não foi possível carregar o resumo do caixa.\n\n{e}"
            )


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
        self.input_email_cliente.setPlaceholderText("Email do cliente (Opcional)")
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
            sucesso, mensagem = cadastrar_cliente(
                nome=nome,
                cpf=cpf,
                email=email
            )

            if not sucesso:
                QMessageBox.critical(self, "Erro", mensagem)
                return

            QMessageBox.information(self, "Sucesso", mensagem)

            self.input_nome_cliente.clear()
            self.input_cpf_cliente.clear()
            self.input_email_cliente.clear()

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

    nome = (
        usuario.get("nome_Usuario")
        or usuario.get("nome_usuario")
        or usuario.get("nomeUsuario")
        or usuario.get("nome")
        or "Não informado"
    )

    cpf = usuario.get("cpf", "Não informado")
    telefone = usuario.get("telefone") or "Não informado"
    email = usuario.get("email") or "Não informado"

    self.lbl_detalhes.setText(
        f"Nome: {nome}\n"
        f"CPF: {cpf}\n"
        f"Telefone: {telefone}\n"
        f"E-mail: {email}"
    )

  def fazer_logout(self):
    SessaoUsuario.encerrar_sessao()
    
    QMessageBox.information(self, "Logout", "Sessão encerrada com sucesso.")
    
    self.app_stack.setCurrentIndex(0)


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

        btn_conexao = QPushButton("  Testar conexão")
        btn_conexao.setMinimumHeight(42)
        btn_conexao.clicked.connect(self.executar_teste_conexao)
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


    def executar_teste_conexao(self):
        try:
            sucesso, mensagem = testar_conexao()

            if sucesso:
                QMessageBox.information(
                    self, "Teste de conexão", mensagem
                )
            else:
                QMessageBox.warning(
                    self, "Falha na conexão", mensagem
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

        self.cupom = QLineEdit()
        self.cupom.setPlaceholderText("Cupom da venda")
        self.cupom.setMinimumHeight(42)
        formulario.addWidget(self.cupom)

        self.cliente_id = QLineEdit()
        self.cliente_id.setPlaceholderText(
            "ID do cliente (opcional)"
        )
        self.cliente_id.setMinimumHeight(42)
        formulario.addWidget(self.cliente_id)

        self.subtotal = QLineEdit()
        self.subtotal.setPlaceholderText(
            "Subtotal (ex.: 150,00)"
        )
        self.subtotal.setMinimumHeight(42)
        formulario.addWidget(self.subtotal)

        self.desconto = QLineEdit()
        self.desconto.setPlaceholderText(
            "Desconto em % (ex.: 10)"
        )
        self.desconto.setMinimumHeight(42)
        formulario.addWidget(self.desconto)

        self.obs = QLineEdit()
        self.obs.setPlaceholderText("Observação (opcional)")
        self.obs.setMinimumHeight(42)
        formulario.addWidget(self.obs)

        principal.addWidget(
            self.frame,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_registrar = QPushButton("Registrar Venda")
        btn_registrar.setFixedSize(160, 40)
        btn_registrar.clicked.connect(self.registrar)
        botoes.addWidget(btn_registrar)

        botoes.addStretch()
        principal.addLayout(botoes)
        principal.addStretch()

    @staticmethod
    def converter_decimal(texto):
        texto = texto.strip()
        texto = texto.replace("R$", "").replace(" ", "")

        if not texto:
            raise ValueError("Preencha os valores obrigatórios.")

        if "," in texto and "." in texto:
            # Exemplo: 1.500,50
            texto = texto.replace(".", "").replace(",", ".")
        else:
            # Aceita 150,50 ou 150.50
            texto = texto.replace(",", ".")

        try:
            valor = Decimal(texto)
        except InvalidOperation:
            raise ValueError("Informe um valor numérico válido.")

        if not valor.is_finite():
            raise ValueError("Informe um valor finito.")

        return valor

    def registrar(self):
        cupom = self.cupom.text().strip()
        cliente_texto = self.cliente_id.text().strip()
        subtotal_texto = self.subtotal.text().strip()
        desconto_texto = self.desconto.text().strip()
        observacao = self.obs.text().strip()

        if not cupom:
            QMessageBox.warning(
                self, "Atenção",
                "Informe o cupom da venda."
            )
            self.cupom.setFocus()
            return

        if not subtotal_texto or not desconto_texto:
            QMessageBox.warning(
                self, "Atenção",
                "Preencha o subtotal e o desconto."
            )
            return

        try:
            # Cliente é opcional.
            if cliente_texto:
                cliente_id = int(cliente_texto)

                if cliente_id <= 0:
                    raise ValueError(
                        "O ID do cliente deve ser positivo."
                    )
            else:
                cliente_id = None

            subtotal = self.converter_decimal(subtotal_texto)
            desconto = self.converter_decimal(desconto_texto)

            if subtotal <= 0:
                raise ValueError(
                    "O subtotal deve ser maior que zero."
                )

            if desconto < 0 or desconto > 100:
                raise ValueError(
                    "O desconto deve estar entre 0 e 100%."
                )

            # Calcula o valor final da venda.
            total = (
                subtotal * (Decimal("100") - desconto)
                / Decimal("100")
            )

            # Obtém o funcionário autenticado.
            usuario = SessaoUsuario.obter_usuario()

            if not usuario:
                QMessageBox.warning(
                    self, "Sessão expirada",
                    "Faça login antes de registrar uma venda."
                )
                return

            # Ajuste a chave conforme o retorno real
            # de app_buscar_funcionario_por_cpf().
            funcionario_id = None

            if isinstance(usuario, dict):
                for chave in (
                    "funcionario_id",
                    "id_funcionario",
                    "idFuncionario",
                    "id"
                ):
                    if usuario.get(chave) is not None:
                        funcionario_id = usuario[chave]
                        break

            if funcionario_id is None:
                QMessageBox.critical(
                    self, "Erro de sessão",
                    "Não foi possível identificar o ID do funcionário "
                    "logado. Verifique os dados retornados pelo banco."
                )
                return

            funcionario_id = int(funcionario_id)

            if funcionario_id <= 0:
                raise ValueError(
                    "O ID do funcionário deve ser positivo."
                )

            # A função retorna (sucesso, mensagem).
            sucesso, mensagem = registrar_venda(
                cupom,
                cliente_id,
                funcionario_id,
                float(subtotal),
                float(desconto),
                float(total),
                observacao
            )

            if not sucesso:
                QMessageBox.critical(
                    self, "Erro ao registrar venda", mensagem
                )
                return

            QMessageBox.information(
                self,
                "Venda registrada",
                f"{mensagem}\n\n"
                f"Subtotal: {formatar_moeda(subtotal)}\n"
                f"Desconto: {desconto}%\n"
                f"Total: {formatar_moeda(total)}"
            )

            self.cupom.clear()
            self.cliente_id.clear()
            self.subtotal.clear()
            self.desconto.clear()
            self.obs.clear()

        except (ValueError, ArithmeticError) as e:
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
                self,
                "Atenção",
                "Informe o valor da compra."
            )
            return

        try:
            # Aceita 150,00; 150.00 e 1.500,00.
            if "," in texto and "." in texto:
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", ".")

            valor = Decimal(texto)

            if not valor.is_finite() or valor <= 0:
                raise ValueError(
                    "O valor deve ser maior que zero."
                )

            # Chama a função importada de conexao.py.
            pontos = fn_calcular_pontos_compra(float(valor))

            if pontos is None:
                self.resultado.setText(
                    "A função não retornou pontos. "
                    "Verifique a implementação em conexao.py."
                )
                return

            self.resultado.setText(
                f"Valor da compra: {formatar_moeda(valor)}\n"
                f"Pontos calculados: {pontos}"
            )

        except (ValueError, ArithmeticError) as e:
            QMessageBox.warning(
                self,
                "Valor inválido",
                str(e)
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao calcular pontos",
                f"Não foi possível calcular os pontos:\n{e}"
            )



class LojaCoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojaCore")
        self.setWindowIcon(QIcon("icon.jpeg"))
        self.setFixedSize(1337, 768)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.tela_login = TelaLogin(self.stack)
        self.tela_cadastro = TelaCadastro(self.stack)
        self.tela_principal = TelaPrincipalSistema(
            app_stack=self.stack
        )

        self.stack.addWidget(self.tela_login)      # Índice 0
        self.stack.addWidget(self.tela_cadastro)   # Índice 1
        self.stack.addWidget(self.tela_principal)  # Índice 2

        self.aplicar_estilo()

        self.stack.setCurrentIndex(0)

    def aplicar_estilo(self):
        self.setStyleSheet("""
            /* ===== ESTILO GLOBAL ===== */
            QWidget {
                background-color: #F1F5F9;
                color: #243447;
                font-family: Arial;
                font-size: 13px;
            }

            /* ===== PAINEL LATERAL ===== */
            #painelLateral {
                background-color: #142D4E;
                border: 1px solid #203F63;
                border-radius: 12px;
            }

            #painelLateral QLabel {
                background-color: transparent;
                color: #FFFFFF;
            }

            #nomeLoja {
                font-size: 21px;
                font-weight: bold;
                color: #FFFFFF;
            }

            #iconeLoja {
                background-color: #203F63;
                border: 1px solid #41658A;
                border-radius: 12px;
            }

            #painelLateral QPushButton {
                background-color: #203F63;
                color: #FFFFFF;
                border: 1px solid transparent;
                border-radius: 7px;
                padding: 10px;
                text-align: left;
            }

            #painelLateral QPushButton:hover {
                background-color: #2D5680;
                border: 1px solid #5B85B0;
            }

            #painelLateral QPushButton:pressed {
                background-color: #10243D;
            }

            /* ===== TÍTULOS ===== */
            #tituloPagina {
                font-size: 23px;
                font-weight: bold;
                color: #142D4E;
                padding: 5px;
            }

            #subtitulo {
                color: #64748B;
                font-size: 14px;
            }

            /* ===== CARDS DO MENU ===== */
            #cardMenu {
                background-color: #FFFFFF;
                border: 1px solid #D8E2EE;
                border-radius: 12px;
            }

            #tituloCard {
                background-color: transparent;
                color: #142D4E;
                font-size: 15px;
                font-weight: bold;
            }

            #descricaoCard {
                background-color: transparent;
                color: #64748B;
            }

            /* ===== CAMPOS DE TEXTO ===== */
            QLineEdit {
                background-color: #FFFFFF;
                color: #243447;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 10px;
                min-height: 20px;
                selection-background-color: #2563A6;
                selection-color: #FFFFFF;
            }

            QLineEdit:focus {
                border: 1px solid #2563A6;
            }

            QLineEdit:disabled {
                background-color: #E2E8F0;
                color: #94A3B8;
            }

            /* ===== BOTÕES GERAIS ===== */
            QPushButton {
                background-color: #2563A6;
                color: #FFFFFF;
                border: 1px solid #2563A6;
                border-radius: 7px;
                padding: 10px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4F85;
                border-color: #1D4F85;
            }

            QPushButton:pressed {
                background-color: #163B64;
            }

            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
                border-color: #CBD5E1;
            }

            /* ===== TABELAS ===== */
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F1F5F9;
                color: #243447;
                border: 1px solid #D8E2EE;
                border-radius: 7px;
                gridline-color: #E2E8F0;
                selection-background-color: #DCEBFA;
                selection-color: #142D4E;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QTableWidget::item:selected {
                background-color: #DCEBFA;
                color: #142D4E;
            }

            QHeaderView::section {
                background-color: #203F63;
                color: #FFFFFF;
                padding: 9px;
                border: none;
                font-weight: bold;
            }

            /* ===== FORMULÁRIOS DE CADASTRO ===== */
            #cadastro {
                background-color: #FFFFFF;
                border: 1px solid #D8E2EE;
                border-radius: 12px;
            }

            #login {
                background-color: #FFFFFF;
                border: 1px solid #D8E2EE;
                border-radius: 12px;
            }

            #cadastroCliente {
                background-color: #FFFFFF;
                border: 1px solid #D8E2EE;
                border-radius: 12px;
            }

            #cadastroCliente QLabel {
                background-color: transparent;
                color: #243447;
            }

            #cadastroCliente QLineEdit {
                background-color: #F8FAFC;
                color: #243447;
                border: 1px solid #CBD5E1;
                border-radius: 7px;
                padding: 10px;
            }

            #cadastroCliente QLineEdit:focus {
                border: 1px solid #2563A6;
            }

            /* ===== INDICADORES DE ESTATÍSTICAS ===== */
            #valor {
                background-color: transparent;
                color: #1D4F85;
                font-size: 20px;
                font-weight: bold;
            }

            /* ===== BARRAS DE ROLAGEM ===== */
            QScrollBar:vertical {
                background-color: #E2E8F0;
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #94A3B8;
                min-height: 25px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #2563A6;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar:horizontal {
                background-color: #E2E8F0;
                height: 10px;
                margin: 0;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal {
                background-color: #94A3B8;
                min-width: 25px;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: #2563A6;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
            }

            /* ===== MENSAGENS E SELEÇÃO ===== */
            QMessageBox {
                background-color: #F1F5F9;
                color: #243447;
            }

            QPlainTextEdit {
                background-color: #FFFFFF;
                color: #243447;
                border: 1px solid #D8E2EE;
                border-radius: 7px;
                padding: 12px;
                selection-background-color: #DCEBFA;
                selection-color: #142D4E;
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
