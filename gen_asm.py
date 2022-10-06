class gen_asm():
    def __init__(self, code):
        self.code = code
        self.asm = []
        self.asm_data = []
        self.get_asm()

    def get_asm(self):
        while len(self.code) != 0:
            i = self.code[0]
            temp = ''
            if i[0] == '=':
                temp += 'MOV AX,'+i[3]+'\n'
                temp += 'MOV '+i[1]+',AX'+'\n'
                self.asm.append(temp)
                del self.code[0]

            elif i[0] == '+':
                temp += 'MOV AX,'+i[1]+'\n'
                temp += 'ADD AX,'+i[2]+'\n'
                del self.code[0]

                i = self.code[0]
                temp += 'MOV '+i[1]+',AX'+'\n'
                del self.code[0]

            elif i[0] == '-':
                temp += 'MOV AX,'+i[1]+'\n'
                temp += 'SUB AX,'+i[2]+'\n'
                del self.code[0]

                i = self.code[0]
                temp += 'MOV '+i[1]+',AX'+'\n'
                del self.code[0]

            elif i[0] == '*':
                temp += 'MOV AX,'+i[1]+'\n'
                temp += 'MOV BX,'+i[2]+'\n'
                temp += 'MUL BX\n'
                del self.code[0]

                i = self.code[0]
                temp += 'MOV '+i[1]+',AX'+'\n'
                del self.code[0]

            elif i[0] == '%':
                temp += 'MOV AX,'+i[1]+'\n'
                temp += 'MOV BX,'+i[2]+'\n'
                temp += 'MUL BX\n'
                del self.code[0]

                i = self.code[0]
                temp += 'MOV '+i[1]+',AX'+'\n'
                del self.code[0]

    def process_data(self, iden, value):
        temp = ''
        temp += 'data segment\n'
        temp += iden + ' db '+value+'\n'
        temp += 'data ends\n'
        self.asm_data.append(temp)
