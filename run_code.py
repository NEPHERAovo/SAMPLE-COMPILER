from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMetaObject
import sys


class run_code_gui(QMainWindow):
    def __init__(self, code):
        super().__init__()
        self.setWindowTitle('run code')
        self.setGeometry(round((1920-800)/2), round((1080-600)/2), 800, 600)
        self.code = code

        self.variable = dict()
        self.code2str()
        self.gui_init()
        # self.run_it(self.code)

    def code2str(self):
        self.code_str = ''
        for j in range(len(self.code)):
            i = self.code[j]
            self.code_str += str(j) + \
                '    ('+i[0]+','+i[1]+','+i[2]+','+i[3]+')\n'

    def gui_init(self):
        layout_main = QHBoxLayout()
        self.code_brower = QTextBrowser()
        self.code_brower.setPlainText(self.code_str)
        layout_main.addWidget(self.code_brower)
        button = QPushButton()
        button.setText('运行')
        button.clicked.connect(lambda: self.run_it(self.code))
        layout_main.addWidget(button)
        self.result_brower = QTextBrowser()
        layout_main.addWidget(self.result_brower)
        widget_main = QWidget()
        widget_main.setLayout(layout_main)
        self.setCentralWidget(widget_main)

    def run_it(self, code):
        self.res_info = ''
        i = 0
        while i < len(code):
            if code[i][0] == '=':
                if code[i][3] in self.variable:
                    res = int(self.variable[code[i][3]])
                elif code[i][3] == 'read()':
                    res, _ = QInputDialog.getText(
                        self, '输入', '输入'+code[i][1]+'的值', QLineEdit.Normal)
                    res = int(res)
                else:
                    res = int(code[i][3])
                self.variable[code[i][1]] = res
                i += 1

            elif code[i][0] == 'j':
                if code[i][3] == 'write()':
                    print(self.variable[code[i][2]])
                    self.res_info += str(self.variable[code[i][2]])+'\n'
                    i += 1
                else:
                    i = int(code[i][3])

            elif code[i][0] == 'j>=':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                if arg1 >= arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j<=':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                if arg1 <= arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j==':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                if arg1 == arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j<':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                if arg1 < arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == '+':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                self.variable[code[i][3]] = arg1+arg2
                i += 1

            elif code[i][0] == '*':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                self.variable[code[i][3]] = arg1*arg2
                i += 1

            elif code[i][0] == '%':
                if code[i][1] in self.variable:
                    arg1 = self.variable[code[i][1]]
                else:
                    arg1 = int(code[i][1])
                if code[i][2] in self.variable:
                    arg2 = self.variable[code[i][2]]
                else:
                    arg2 = int(code[i][2])
                self.variable[code[i][3]] = arg1 % arg2
                i += 1
        self.result_brower.setPlainText(self.res_info)


if __name__ == '__main__':
    app = QApplication([])
    ex = run_code_gui([['=', 'j', '_', 'read()']])
    ex.show()
    sys.exit(app.exec())
