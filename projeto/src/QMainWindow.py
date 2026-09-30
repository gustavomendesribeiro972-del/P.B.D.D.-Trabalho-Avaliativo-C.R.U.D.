# Parei em:
# https://www.pythonguis.com/tutorials/pyqt6-signals-slots-events/

#OBS: EDITAR PARA FICAR CONFORME O PROJETO...

import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

class JanelaMain(QMainWindow):
        def __init__(self):
                super().__init__()

                self.setWindowTitle("Ygona Imensa")
                button = QPushButton("Aperte")
                button.setCheckable(True)
                button.clicked.connect(self.clique_do_botao)

                self.setFixedSize(QSize(1200, 900))

                self.setCentralWidget(button)
        def clique_do_botao(self):
                print("Click or Clique?")

app = QApplication(sys.argv)

janela = JanelaMain()
janela.show()

app.exec()
