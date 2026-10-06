# Parei em:
# https://www.pythonguis.com/tutorials/pyqt6-signals-slots-events/

#OBS: EDITAR PARA FICAR CONFORME O PROJETO...
import sys
from decimal import Decimal
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Importa as funções que você já testou no terminal
from conexao import (
    cadastrar_cliente,
    listar_vendas_recentes,
    registrar_venda,
    testar_conexao,
)


class LojaCoreApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LojaCore - Sistema de Lojas")
        self.resize(1167, 718)

        # Container Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- CABEÇALHO ---
        self.lbl_status = QLabel("Status do Banco: Verificando...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(self.lbl_status)

        # --- ÁREA DE FORMULÁRIOS (Lado a Lado) ---
        forms_layout = QHBoxLayout()

        # 1. Formulário de Cadastro de Perfil / Cliente
        group_cliente_layout = QFormLayout()
        self.txt_cli_nome = QLineEdit()
        self.txt_cli_cpf = QLineEdit()
        self.txt_cli_email = QLineEdit()
        btn_salvar_cliente = QPushButton("👤 Cadastrar Cliente")
        btn_salvar_cliente.clicked.connect(self.salvar_cliente)

        group_cliente_layout.addRow("<b>CADASTRO DE CLIENTE</b>", QLabel(""))
        group_cliente_layout.addRow("Nome:", self.txt_cli_nome)
        group_cliente_layout.addRow("CPF:", self.txt_cli_cpf)
        group_cliente_layout.addRow("E-mail:", self.txt_cli_email)
        group_cliente_layout.addRow(btn_salvar_cliente)

        forms_layout.addLayout(group_cliente_layout)

        # Divisor visual
        forms_layout.addSpacing(20)

        # 2. Formulário de Registro de Venda
        group_venda_layout = QFormLayout()
        self.txt_venda_cupom = QLineEdit()
        self.txt_venda_cliente_id = QLineEdit()
        self.txt_venda_cliente_id.setPlaceholderText("Deixe em branco p/ NULL")
        self.txt_venda_func_id = QLineEdit("2")
        self.txt_venda_subtotal = QLineEdit("100.00")
        self.txt_venda_desconto = QLineEdit("10.00")
        btn_salvar_venda = QPushButton("🛒 Registrar Venda (Procedure)")
        btn_salvar_venda.clicked.connect(self.salvar_venda)

        group_venda_layout.addRow("<b>NOVA VENDA</b>", QLabel(""))
        group_venda_layout.addRow("Nº Cupom:", self.txt_venda_cupom)
        group_venda_layout.addRow("ID Cliente:", self.txt_venda_cliente_id)
        group_venda_layout.addRow("ID Funcionário:", self.txt_venda_func_id)
        group_venda_layout.addRow("Subtotal (R$):", self.txt_venda_subtotal)
        group_venda_layout.addRow("Desconto (R$):", self.txt_venda_desconto)
        group_venda_layout.addRow(btn_salvar_venda)

        forms_layout.addLayout(group_venda_layout)
        main_layout.addLayout(forms_layout)

        # --- TABELA DE VENDAS RECENTES ---
        main_layout.addWidget(
            QLabel("<b>📊 Últimas Vendas Registradas (View/Select)</b>")
        )
        self.tabela_vendas = QTableWidget()
        self.tabela_vendas.setColumnCount(6)
        self.tabela_vendas.setHorizontalHeaderLabels(
            ["ID", "Cupom", "ID Cliente", "ID Func.", "Total", "Status"]
        )
        self.tabela_vendas.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        main_layout.addWidget(self.tabela_vendas)

        # Inicializa o status do banco e carrega a tabela
        self.verificar_conexao()
        self.atualizar_tabela()

    def verificar_conexao(self):
        ok, msg = testar_conexao()
        if ok:
            self.lbl_status.setText("🟢 Conectado ao PostgreSQL")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status.setText("🔴 Falha na Conexão com o Banco")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")

    def salvar_cliente(self):
        nome = self.txt_cli_nome.text().strip()
        cpf = self.txt_cli_cpf.text().strip()
        email = self.txt_cli_email.text().strip()

        if not nome:
            QMessageBox.warning(
                self, "Aviso", "O nome do cliente é obrigatório!"
            )
            return

        sucesso, msg = cadastrar_cliente(nome, cpf, email)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.txt_cli_nome.clear()
            self.txt_cli_cpf.clear()
            self.txt_cli_email.clear()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def salvar_venda(self):
        cupom = self.txt_venda_cupom.text().strip() or "CUP-GUI-001"
        cli_id = (
            int(self.txt_venda_cliente_id.text())
            if self.txt_venda_cliente_id.text().isdigit()
            else None
        )
        func_id = (
            int(self.txt_venda_func_id.text())
            if self.txt_venda_func_id.text().isdigit()
            else 2
        )

        try:
            subtotal = float(self.txt_venda_subtotal.text())
            desconto = float(self.txt_venda_desconto.text())
            total = max(0.0, subtotal - desconto)
        except ValueError:
            QMessageBox.warning(
                self, "Erro", "Digite valores numéricos válidos nos valores!"
            )
            return

        sucesso, msg = registrar_venda(
            cupom,
            cli_id,
            func_id,
            subtotal,
            desconto,
            total,
            "Venda efetuada via PyQt6",
        )

        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.atualizar_tabela()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def atualizar_tabela(self):
        vendas = listar_vendas_recentes()
        self.tabela_vendas.setRowCount(0)

        if not vendas:
            return

        for row_idx, v in enumerate(vendas):
            self.tabela_vendas.insertRow(row_idx)
            cliente_txt = (
                str(v.cliente_id) if v.cliente_id is not None else "ANÔNIMO"
            )

            self.tabela_vendas.setItem(
                row_idx, 0, QTableWidgetItem(str(v.id_venda))
            )
            self.tabela_vendas.setItem(
                row_idx, 1, QTableWidgetItem(str(v.numero_cupom))
            )
            self.tabela_vendas.setItem(
                row_idx, 2, QTableWidgetItem(cliente_txt)
            )
            self.tabela_vendas.setItem(
                row_idx, 3, QTableWidgetItem(str(v.funcionario_id))
            )
            self.tabela_vendas.setItem(
                row_idx, 4, QTableWidgetItem(f"R$ {v.total:.2f}")
            )
            self.tabela_vendas.setItem(
                row_idx, 5, QTableWidgetItem(str(v.status))
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LojaCoreApp()
    window.show()
    sys.exit(app.exec())