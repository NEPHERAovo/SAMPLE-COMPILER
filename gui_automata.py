from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMetaObject
import automata
import sys


class GUI_automata(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('automata')
        self.setGeometry(round((1920-1024)/2), round((1080-200)/2), 1024, 200)

        layout_main = QVBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('input regular expression')
        self.line_edit.setObjectName("editor")
        self.flag = 1
        self.error = 0

        layout_main.addWidget(self.line_edit)
        self.path = 'D:/Softwares/Python/'

        layout_button = QHBoxLayout()
        button_nfa = QPushButton()
        button_nfa.setText('REG->NFA')
        button_nfa.clicked.connect(lambda: self.reg2nfa())
        layout_button.addWidget(button_nfa)
        button_dfa = QPushButton()
        button_dfa.setText('NFA->DFA')
        button_dfa.clicked.connect(lambda: self.nfa2dfa())
        layout_button.addWidget(button_dfa)
        button_mdfa = QPushButton()
        button_mdfa.setText('DFA->MDFA')
        button_mdfa.clicked.connect(lambda: self.dfa2mdfa())
        layout_button.addWidget(button_mdfa)

        widget_button = QWidget()
        widget_button.setLayout(layout_button)
        layout_main.addWidget(widget_button)

        self.pic_display = QLabel()
        layout_main.addWidget(self.pic_display)

        widget_main = QWidget()
        layout_main.addStretch(1)
        widget_main.setLayout(layout_main)
        self.setCentralWidget(widget_main)

        QMetaObject.connectSlotsByName(self)

    def do_it(self):
        try:
            self.flag = 0
            regex = self.line_edit.text()
            self.display_temp = automata.gui_display(regex)
            self.display_temp.regex_nfa()
            self.display_temp.nfa_dfa()
            self.display_temp.dfa_mdfa()
            self.error = 0
        except:
            msg = QMessageBox(QMessageBox.Critical, '错误', '正规式输入有误')
            msg.exec_()
            self.error = 1

    def reg2nfa(self):
        if self.flag == 1:
            self.do_it()
        if self.error == 0:
            pixmap = QPixmap(self.path+'nfa.png')
            self.pic_display.setPixmap(pixmap)
            self.pic_display.setAlignment(Qt.AlignCenter)

    def nfa2dfa(self):
        if self.flag == 1:
            self.do_it()
        if self.error == 0:
            pixmap = QPixmap(self.path+'dfa.png')
            self.pic_display.setPixmap(pixmap)
            self.pic_display.setAlignment(Qt.AlignCenter)

    def dfa2mdfa(self):
        if self.flag == 1:
            self.do_it()
        if self.error == 0:
            pixmap = QPixmap(self.path+'mdfa.png')
            self.pic_display.setPixmap(pixmap)
            self.pic_display.setAlignment(Qt.AlignCenter)

    def on_editor_textChanged(self):
        self.flag = 1


if __name__ == '__main__':
    app = QApplication([])
    ex = GUI_automata()
    ex.show()
    sys.exit(app.exec())
