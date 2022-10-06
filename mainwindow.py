from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from codeditor import QCodeEditor
from gui_automata import *
import os
import sys
import time
import lexer2
from ll1predict import ll1_predict
from generate_code import generate_code
from run_code import run_code_gui
import ply_lexer


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'compiler'
        self.width = 800
        self.height = 600
        self.left = round((1920-800)/2)
        self.top = round((1080-600)/2)

        self.dialog = ''
        self.path = None
        self.flag = 0
        self.ll1 = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        leftWidget = self.createLeftWidget()
        rightWidget = self.createRightWidget()

        mainMenu = self.createMenu()

        mainLayout = QHBoxLayout()
        mainLayout.setMenuBar(mainMenu)
        mainLayout.addWidget(leftWidget)
        mainLayout.addWidget(rightWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        QMetaObject.connectSlotsByName(self)

    def createLeftWidget(self):
        layoutLeft = QVBoxLayout()

        code_label = QLabel()
        code_label.setText('code')
        layoutLeft.addWidget(code_label)

        self.editor = QCodeEditor()
        self.editor.setObjectName("editor")
        layoutLeft.addWidget(self.editor)

        leftWidget = QWidget()
        leftWidget.setLayout(layoutLeft)

        return leftWidget

    def createRightWidget(self):
        layoutRight = QVBoxLayout()

        output_label = QLabel()
        output_label.setText('output')
        layoutRight.addWidget(output_label)

        self.table = QTableWidget(0, 4)
        # self.table.setHorizontalHeaderLabels(['内容', '类型', '行号', '列号'])
        self.table.horizontalHeader().setSectionResizeMode(1)
        layoutRight.addWidget(self.table)

        layoutButton = QHBoxLayout()

        # buttonWidget = QWidget()
        # buttonWidget.setLayout(layoutButton)
        # layoutRight.addWidget(buttonWidget)

        dialog_label = QLabel()
        dialog_label.setText('dialog')
        layoutRight.addWidget(dialog_label)

        self.dialog_window = QTextBrowser()
        layoutRight.addWidget(self.dialog_window)

        rightWidget = QWidget()
        rightWidget.setLayout(layoutRight)

        return rightWidget

    def createMenu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')

        openButton = QAction('Open', self)
        openButton.setStatusTip("open a code file")
        openButton.triggered.connect(self.openFile)
        fileMenu.addAction(openButton)

        saveButton = QAction('Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setStatusTip("save file")
        saveButton.triggered.connect(self.saveFile)
        fileMenu.addAction(saveButton)

        lexer_Menu = mainMenu.addMenu('词法分析')
        button_manual = QAction('手动', self)
        button_manual.triggered.connect(lambda: self.table_display())
        button_auto = QAction('自动', self)
        button_auto.triggered.connect(lambda: self.table_display_auto())
        lexer_Menu.addAction(button_manual)
        lexer_Menu.addAction(button_auto)

        show_Menu = mainMenu.addMenu('算法展示')
        automata_button = QAction('Automata', self)
        automata_button.triggered.connect(lambda: self.open_automata_window())
        show_Menu.addAction(automata_button)

        grammar_Menu = mainMenu.addMenu('语法分析')
        button_LL1 = QAction('LL(1)', self)
        button_LL1.triggered.connect(lambda: self.ll1_predict())
        grammar_Menu.addAction(button_LL1)
        button_code = QAction('生成四元式', self)
        button_code.triggered.connect(lambda: self.get_code())
        grammar_Menu.addAction(button_code)

        run_Menu = mainMenu.addMenu('运行')
        button_run = QAction('运行', self)
        button_run.triggered.connect(lambda: self.run_code())
        run_Menu.addAction(button_run)
        # toolsMenu = mainMenu.addMenu('Tools')
        # helpMenu = mainMenu.addMenu('Help')

        return mainMenu

    def open_automata_window(self):
        ex_2 = GUI_automata()
        ex_2.show()

    def openFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "open file", "", "ALL FILES (*.*);;TXT FILES (*.txt)")

        if path:
            text = open(path, 'r', encoding='utf-8').read()
            self.path = path
            self.editor.setPlainText(text)
            time_temp = time.strftime("[%H:%M:%S]  ")
            self.dialog += time_temp + 'successfully opened file ' + path + '\n'
            self.dialog_show()

        self.flag = 0

    def saveFile(self):
        self.flag = 0

        text = self.editor.toPlainText()

        if self.path:
            open(self.path, 'w').write(text)
            time_temp = time.strftime("[%H:%M:%S]  ")
            self.dialog += time_temp + 'successfully saved file to ' + self.path + '\n'
            self.dialog_show()
        else:
            time_temp = time.strftime("[%H:%M:%S]  ")
            self.dialog += time_temp + 'no path chosen, failed saving \n'
            self.dialog_show()

    def table_display_auto(self):
        self.table.setHorizontalHeaderLabels(['内容', '类型', '行号', '列号'])
        self.dialog = ''
        self.table.setRowCount(0)
        if self.path and self.flag == 0:
            result, error_list = ply_lexer.open_file(self.path)
        else:
            temp = self.editor.toPlainText()
            open('temp.dat', 'w', encoding='utf-8').write(temp)
            result, error_list = ply_lexer.open_file('temp.dat')
        i = 0
        while result:
            row = self.table.rowCount()
            self.table.setRowCount(row+1)
            self.table.setItem(i, 0, QTableWidgetItem(result[0][0]))
            self.table.setItem(i, 1, QTableWidgetItem(result[0][1]))
            self.table.setItem(i, 2, QTableWidgetItem(result[0][2]))
            i += 1
            del result[0]
        self.dialog += error_list
        self.dialog_show()

    def table_display(self):
        self.table.setHorizontalHeaderLabels(['内容', '类型', '行号', '列号'])
        self.dialog = ''
        self.table.setRowCount(0)
        if self.path and self.flag == 0:
            lex = lexer2.lexer(self.path)
            result = lex.result
            self.result = result
        else:
            temp = self.editor.toPlainText()
            open('temp.dat', 'w', encoding='utf-8').write(temp)
            lex = lexer2.lexer('temp.dat')
            result = lex.result
            self.result = result
        for i in range(len(result)):
            row = self.table.rowCount()
            self.table.setRowCount(row+1)
            self.table.setItem(i, 0, QTableWidgetItem(result[i][0]))
            self.table.setItem(i, 1, QTableWidgetItem(result[i][1]))
            self.table.setItem(i, 2, QTableWidgetItem(result[i][2]))
            self.table.setItem(i, 3, QTableWidgetItem(result[i][3]))
        self.dialog += lex.warnings
        self.dialog_show()

    def ll1_predict(self):
        if len(self.result) != 0:
            if self.flag == 1:
                self.table_display()
            self.ll1 = ll1_predict(self.result)
            if self.ll1.welldone == 1:
                msg = QMessageBox(QMessageBox.NoIcon, '成功', '词法分析通过')
                msg.exec_()
            else:
                msg = QMessageBox(QMessageBox.Critical, '错误', '词法分析未通过')
                msg.exec_()
        else:
            msg = QMessageBox(QMessageBox.Critical, '错误', '没有词法分析结果')
            msg.exec_()

    def get_code(self):
        try:
            self.table.setHorizontalHeaderLabels(['', '', '', ''])
            self.a = generate_code(self.ll1.ast.root, self.ll1.end)
            if len(self.a.warn) != 0:
                msg = QMessageBox(QMessageBox.Critical, '错误', '存在语义错误')
                msg.exec_()
                self.dialog = ''
                for i in self.a.warn:
                    self.dialog += i+'\n'
                self.dialog_show()
            else:
                self.table.setRowCount(0)
                for i in range(len(self.a.code)-1):
                    row = self.table.rowCount()
                    self.table.setRowCount(row+1)
                    self.table.setItem(
                        i, 0, QTableWidgetItem(self.a.code[i][0]))
                    self.table.setItem(
                        i, 1, QTableWidgetItem(self.a.code[i][1]))
                    self.table.setItem(
                        i, 2, QTableWidgetItem(self.a.code[i][2]))
                    if isinstance(self.a.code[i][3], int):
                        self.table.setItem(i, 3, QTableWidgetItem(
                            str(int(self.a.code[i][3])+1)))
                    else:
                        self.table.setItem(
                            i, 3, QTableWidgetItem(self.a.code[i][3]))
        except:
            msg = QMessageBox(QMessageBox.Critical, '错误', '没有语法分析结果')
            msg.exec_()

    # def get_asm(self):
    #     b = gen_asm(self.a.code)

    def run_code(self):
        try:
            ex_3 = run_code_gui(self.a.code)
            ex_3.show()
        except:
            msg = QMessageBox(QMessageBox.Critical, '错误', '没有四元式')
            msg.exec_()

    def dialog_show(self):
        self.dialog_window.setText(self.dialog)

    # @pyqtSlot()
    def on_editor_textChanged(self):
        self.flag = 1

    def closeEvent(self, a0: QCloseEvent) -> None:
        if os.path.exists('temp.dat'):
            os.remove('temp.dat')
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication([])

    ex = GUI()

    ex.show()

    sys.exit(app.exec())
