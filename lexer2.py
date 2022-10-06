import time


class lexer:
    def __init__(self, path):
        self.init_variable(path)
        self.open_file()
        self.recognize()
        print(self.result)
        print(self.warnings)

    def init_variable(self, path):
        self.text = None
        self.line = 0
        self.row = 0
        self.path = path
        self.status = 'a'

        self.cur = None
        self.temp = ''
        self.result = []
        self.warnings = ''

        self.letter_list = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}
        self.number_list = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
        self.keyword_list = {'auto', 'double', 'int', 'struct', 'break', 'else', 'long', 'switch', 'case', 'enum',
                             'register', 'typedef', 'char', 'extern', 'return', 'union', 'const', 'float', 'short',
                             'unsigned', 'continue', 'for', 'signed', 'void', 'default', 'goto', 'sizeof', 'volatile',
                             'do', 'if', 'while', 'static', 'func'}
        self.board_char_list = {';', ',', '.'}
        self.brackets_list = {'{', '}', '[', ']', '(', ')'}

    def is_letter(self):
        return self.cur in self.letter_list

    def is_number(self):
        return self.cur in self.number_list

    def is_keyword(self):
        return self.temp in self.keyword_list

    def is_board(self):
        return self.cur in self.board_char_list

    def is_brackets(self):
        return self.cur in self.brackets_list

    def is_left_brackets(self):
        if self.cur == '{' or self.cur == '[' or self.cur == '(':
            return True
        else:
            return False

    def is_empty(self):
        if self.cur == ' ' or self.cur == '\n' or self.cur == '\t':
            return True
        else:
            return False

    def is_close(self):
        if self.brackets[len(self.brackets)-1][0] == '{':
            if self.cur == '}':
                return True
            else:
                return False
        elif self.brackets[len(self.brackets)-1][0] == '[':
            if self.cur == ']':
                return True
            else:
                return False
        elif self.brackets[len(self.brackets)-1][0] == '(':
            if self.cur == ')':
                return True
            else:
                return False

    def getchar(self):
        if self.row == len(self.text[self.line]):
            if self.line + 1 == len(self.text):
                self.cur = 'EOF'
                return
            else:
                self.line += 1
                self.row = 0
        self.cur = self.text[self.line][self.row]
        self.row += 1
        self.temp += self.cur

    def backward(self):
        if self.flag_eof == False:
            self.temp = self.temp[:-1]
            self.row -= 2
            self.cur = self.text[self.line][self.row]
            self.row += 1

    def save(self, category):
        if category == 'self':
            category = self.temp.lower()
        temp_result = ['', '', '', '']
        temp_result[0] = self.temp
        temp_result[1] = category
        temp_result[2] = str(self.line+1)
        temp_result[3] = str(self.row-len(self.temp)+1)
        if category != 'note':
            self.result.append(temp_result.copy())
        self.status = 'a'
        self.temp = ''

    def warning(self, category):
        self.warnings += time.strftime("[%H:%M:%S]  ")
        self.warnings += self.temp + ' at line ' + \
            str(self.line+1) + ' row ' + str(self.row-len(self.temp))
        if category == 0:
            self.warnings += ': failed recognizing char\n'
        elif category in [2, 3]:
            self.warnings += ': brackets not close\n'
        elif category == 4:
            self.warnings += ': no left bracket\n'
        elif category == 5:
            self.warnings += ': illegal identifier\n'
        elif category == 6:
            self.warnings += ': note not close\n'
        elif category == 7:
            self.warnings += ': illegal octal number\n'
        elif category == 8:
            self.warnings += ': illegal hex number\n'
        elif category == 9:
            self.warnings += ': illegal number char\n'
        self.status = 'a'
        self.temp = ''

    def status_a(self):
        if self.is_letter() or self.cur == '_':
            self.status = 'b'

        elif self.is_number():
            if self.cur == '0':
                self.getchar()
                if self.cur in ['x', 'X']:
                    self.status = 'c16'
                    return
                elif self.is_number():
                    self.backward()
                    self.status = 'c8'
                elif self.cur == '.':
                    self.dot_num += 1
                    self.status = 'c'
                else:
                    self.backward()
                    self.save('number')
            else:
                self.status = 'c'

        elif self.cur in ['\'', '\"']:
            temp_quote = self.cur
            self.getchar()
            while self.cur != temp_quote:
                self.getchar()
                if self.cur == 'EOF':
                    self.warning(2)
                    self.flag_eof = True
                    return
            if self.cur == temp_quote:
                self.save('string')

        elif self.is_board():
            self.save('self')

        elif self.is_brackets():
            if self.brackets:
                if self.is_left_brackets():
                    self.save('self')
                    temp = [self.cur, self.line, self.row]
                    self.brackets.append(temp)
                elif self.is_close():
                    self.save('self')
                    self.brackets.pop()
                else:
                    self.warning(4)
            else:
                self.save('self')
                temp = [self.cur, self.line, self.row]
                self.brackets.append(temp)

        elif self.cur == '/':
            self.status = 'd'

        elif self.cur in ['\\', '#', ':', '!', '?', '~', '^']:
            self.save(self.cur)

        elif self.cur in ['+', '-', '*', '=', '%', '&', '|', '<', '>']:
            self.status = 'op'
            self.operator = self.cur

        elif self.is_empty():
            self.temp = self.temp[:-1]

        else:
            self.warning(0)

    def status_b(self):
        if self.is_letter() or self.is_number() or self.cur == '_':
            return
        else:
            self.backward()
            if self.is_keyword():
                self.save('self')
            else:
                self.save('identifier')

    def status_c(self):
        if self.is_number():
            return

        elif self.cur in ['e', 'E']:
            if self.e_num >= 1:
                self.warning(9)
            else:
                self.e_num += 1

        elif self.cur == '+':
            if self.plus_num >= 1:
                self.warning(9)
            else:
                self.plus_num += 1

        elif self.cur == '.':
            if self.dot_num >= 1:
                self.warning(9)
            else:
                self.dot_num += 1

        elif self.is_letter() or self.cur == '_':
            self.warning(5)

        else:
            self.backward()
            self.save('number')
            self.dot_num = 0
            self.e_num = 0
            self.plus_num = 0

    def status_c8(self):
        if self.is_number():
            if self.cur >= '0' and self.cur <= '7':
                return
            else:
                self.warning(7)
        else:
            self.backward()
            self.save('oct num')

    def status_c16(self):
        if self.is_number():
            return
        if self.is_letter():
            if self.cur >= 'a' and self.cur <= 'f':
                return
            elif self.cur >= 'A' and self.cur <= 'F':
                return
            else:
                self.warning(8)
        else:
            self.backward()
            self.save('hex num')

    def status_op(self):
        if self.cur in ['=', self.operator]:
            self.save('self')
        else:
            self.backward()
            self.save('self')

    def status_d(self):
        if self.cur == '=':
            self.save('double op')
        elif self.cur == '/':
            while self.cur not in ['EOF', '\n']:
                self.getchar()
            self.save('note')
        elif self.cur == '*':
            while True:
                self.getchar()
                if self.cur == '*':
                    self.getchar()
                    if self.cur == '/':
                        self.save('note')
                        break
                elif self.cur == 'EOF':
                    self.warning(6)
                    break
        else:
            self.backward()
            self.save('op')

    def recognize(self):
        self.flag_eof = False
        self.brackets = []
        self.dot_num = 0
        self.e_num = 0
        self.plus_num = 0
        while True:
            if self.flag_eof:
                if self.brackets:
                    temp = self.brackets.pop()
                    self.cur = temp[0]
                    self.line = temp[1]
                    self.row = temp[2]
                    self.warning(2)
                break
            self.getchar()
            if self.cur == 'EOF':
                self.cur = ' '
                self.flag_eof = True
            if self.status == 'a':
                self.status_a()
            elif self.status == 'b':
                self.status_b()
            elif self.status == 'c':
                self.status_c()
            elif self.status == 'd':
                self.status_d()
            elif self.status == 'c8':
                self.status_c8()
            elif self.status == 'c16':
                self.status_c16()
            elif self.status == 'op':
                self.status_op()

    def open_file(self):
        fp = open(self.path, 'r', encoding='utf-8-sig')
        self.text = fp.readlines()
        # self.text = []
        # self.text.append('123')


if __name__ == '__main__':
    a = lexer('a')
