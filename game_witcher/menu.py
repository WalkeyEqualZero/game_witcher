from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
import logging
import sys
import os


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_menu.ui', self)
        self.new_game.clicked.connect(self.start_game)
        self.setWindowTitle('The Witcher 4: Flat World')

    def start_game(self):
        os.system('python game.py')
        sys.exit(app.exec_())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())