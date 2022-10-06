import copy
#from run_code import run_code


class code_blocks:
    def __init__(self):
        self.variable_list = []
        self.variable_type_list = []
        self.func_list = []
        self.func_type_list = []
        self.lines = []


class generate_code:
    def __init__(self, ast, end):
        self.ast = ast
        self.temp = []
        self.result = []
        self.temp_variable = []
        self.end = end
        self.get_tree(ast)
        self.code = []
        self.warn = []
        print(self.result)
        self.result_copy = self.result[:]
        self.code_block = self.first_view(code_blocks())
        print(self.code_block)
        self.rewrite_stack = []
        self.rewrite_add = []
        self.circle_start = []
        block_temp = copy.deepcopy(self.code_block)
        self.second_view(block_temp)
        while len(self.rewrite_stack) != 0:
            self.re_write()
        for i in range(len(self.code)):
            print(str(i)+' ', end='')
            print(self.code[i])
        #a = run_code(self.code)

    def get_tree(self, node):
        if len(node.children) == 0:
            return
        else:
            for i in reversed(node.children):
                if isinstance(i.ele, list):
                    self.temp.append(i.ele[0]+':'+i.ele[1])
                else:
                    if i.ele in self.end:
                        if i.ele in ['{', '}', ';']:
                            if len(self.temp) > 0:
                                self.result.append(self.temp)
                            if i.ele == '}':
                                self.result.append('}')
                            self.temp = []
                        else:
                            self.temp.append(i.ele)
                self.get_tree(i)

    def first_view(self, block):
        code_block = code_blocks()
        code_block.variable_list = block.variable_list[:]
        code_block.variable_type_list = block.variable_type_list[:]
        code_block.func_list = block.func_list[:]
        code_block.func_type_list = block.func_type_list[:]
        while len(self.result) != 0:
            i = self.result[0]
            if i[0] in ['int', 'char', 'double', 'float', 'long']:
                if '=' in i:
                    temp_index = i.index('=')
                    for k in i[1:temp_index]:
                        k = k.split(':')
                        if k[0] == 'identifier':
                            for j in code_block.variable_list:
                                if k[0] == j:
                                    print('重复定义变量'+k[0])
                                    self.warn.append('重复定义变量'+k[0])
                            code_block.variable_list.append(k[1])
                            code_block.variable_type_list.append(i[0])
                else:
                    for k in i[1:]:
                        k = k.split(':')
                        if k[0] == 'identifier':
                            for j in code_block.variable_list:
                                if k[0] == j:
                                    print('重复定义变量'+k[0])
                                    self.warn.append('重复定义变量'+k[0])
                            code_block.variable_list.append(k[1])
                            code_block.variable_type_list.append(i[0])
                code_block.lines.append(i)
                del self.result[0]
            elif i[0].split(':')[0] == 'identifier':
                code_block.lines.append(i)
                del self.result[0]
            elif i[0] == 'func':
                code_block.func_list.append(i[2])
                code_block.func_type_list.append(i[1])
                del self.result[0]
                code_block.lines.append(self.first_view(code_block))
            elif i[0] in ['if', 'while']:
                code_block.lines.append(i)
                del self.result[0]
                code_block.lines.append(self.first_view(code_block))
            elif i[0] == 'else':
                if len(i) > 1:
                    if i[1] == 'if':
                        code_block.lines.append('else')
                        code_block.lines.append(i[1:])
                        del self.result[0]
                        code_block.lines.append(self.first_view(code_block))
                else:
                    code_block.lines.append(i)
                    del self.result[0]
                    code_block.lines.append(self.first_view(code_block))
            elif i[0] == 'for':
                for j in range(3):
                    code_block.lines.append(self.result[0])
                    del self.result[0]
                code_block.lines.append(self.first_view(code_block))
            elif i[0] == '}':
                del self.result[0]
                return code_block
        return code_block

    def second_view(self, block):
        while len(block.lines) != 0:
            i = block.lines[0]
            if isinstance(i, code_blocks):
                self.second_view(i)
                del block.lines[0]
            else:
                temp = i[0].split(':')
                if i[0] in ['int', 'char', 'double', 'float', 'long', 'func']:
                    if '=' not in i:
                        del block.lines[0]
                    else:
                        temp_index = i.index('=')
                        if '(' in i:
                            self.process_equal(
                                i[temp_index-1].split(':')[1], i[temp_index+1].split(':')[1]+'()')
                        else:
                            self.process_equal(
                                i[temp_index-1].split(':')[1], i[temp_index+1].split(':')[1])
                        del block.lines[0]

                elif temp[0] == 'identifier':
                    if temp[1] in block.variable_list:
                        phrase = i[2:]
                        if len(phrase) == 1 or phrase[1] == '(':
                            if len(phrase) > 1:
                                self.process_equal(
                                    temp[1], phrase[0].split(':')[1]+'()')
                            else:
                                self.process_equal(
                                    temp[1], phrase[0].split(':')[1])
                            del block.lines[0]
                        else:
                            self.process_op(
                                phrase[0].split(':')[1], phrase[2].split(':')[1], phrase[1], temp[1])
                            del block.lines[0]
                    elif temp[1] == 'write':
                        self.code.append(self.gen_code(
                            'j', '_', i[2].split(':')[1], 'write()'))
                        del block.lines[0]
                    else:
                        print('identifier not defined')
                        self.warn.append('identifier not defined :'+temp[1])
                        del block.lines[0]

                elif i[0] == 'if':
                    # IF语句后需要重填
                    self.process_if(i[2].split(':')[1],
                                    i[4].split(':')[1], i[3])
                    del block.lines[0]
                    self.second_view(block.lines[0])

                    temp_code = self.gen_code(
                        'j', '_', '_', str(len(self.code)+1))
                    self.code.append(temp_code)
                    self.rewrite_add[-1][1] = str(len(self.code))

                    del block.lines[0]

                    if len(block.lines) > 0:

                        if block.lines[0] == 'else' or block.lines[0][0] == 'else':
                            del block.lines[0]

                            if isinstance(block.lines[0], code_blocks):

                                self.rewrite_stack.append(temp_code)
                                self.rewrite_add.append(
                                    [str(len(self.code)), ''])
                                self.second_view(block.lines[0])
                            else:
                                continue

                            temp_code = self.gen_code(
                                'j', '_', '_', str(len(self.code)+1))
                            self.code.append(temp_code)

                            self.rewrite_add[-1][1] = str(len(self.code))

                            del block.lines[0]
                            self.re_write()
                            self.re_write()
                        else:
                            self.code.append(self.gen_code(
                                'j', '_', '_', str(len(self.code)+1)))
                            self.rewrite_add[-1][1] = str(len(self.code))
                            self.re_write()
                    else:
                        self.re_write()

                elif i[0] == 'while':
                    self.circle_start.append(str(len(self.code)))
                    self.process_if(i[2].split(':')[1],
                                    i[4].split(':')[1], i[3])
                    del block.lines[0]
                    self.second_view(block.lines[0])

                    temp_code = self.gen_code(
                        'j', '_', '_', self.circle_start.pop())
                    self.code.append(temp_code)
                    self.rewrite_add[-1][1] = str(len(self.code))

                    del block.lines[0]
                    self.re_write()

                elif i[0] == 'for':
                    self.process_equal(i[2].split(':')[1], i[4].split(':')[1])
                    del block.lines[0]
                    self.circle_start.append(str(len(self.code)))
                    self.process_if(block.lines[0][0].split(':')[1],
                                    block.lines[0][2].split(':')[1], block.lines[0][1])
                    del block.lines[0]

                    self.process_op(
                        block.lines[0][2].split(':')[1], block.lines[0][4].split(':')[1], block.lines[0][3], block.lines[0][0].split(':')[1])
                    temp1 = self.code.pop()
                    temp2 = self.code.pop()
                    del block.lines[0]
                    self.second_view(block.lines[0])
                    self.code.append(temp2)
                    self.code.append(temp1)

                    temp_code = self.gen_code(
                        'j', '_', '_', self.circle_start.pop())
                    self.code.append(temp_code)
                    self.rewrite_add[-1][1] = str(len(self.code))

                    del block.lines[0]
                    self.re_write()

    def gen_code(self, op, arg1, arg2, result):
        # return '('+op+', '+arg1+', '+arg2+', '+result+')'
        return [op, arg1, arg2, result]

    def process_equal(self, res, num):
        self.code.append(self.gen_code('=', res, '_', num))

    def process_op(self, arg1, arg2, op, res):
        self.temp_variable.append('t'+str(len(self.temp_variable)))
        self.code.append(self.gen_code(op, arg1, arg2, self.temp_variable[-1]))
        self.code.append(self.gen_code('=', res, '_', self.temp_variable[-1]))

    def process_if(self, arg1, arg2, op):
        self.code.append(self.gen_code(
            'j'+op, arg1, arg2, str(len(self.code)+2)))
        temp_code = self.gen_code('j', '_', '_', str(len(self.code)+1))
        self.code.append(temp_code)
        self.rewrite_stack.append(temp_code)
        self.rewrite_add.append([str(len(self.code)), ''])

    def re_write(self):
        temp = self.rewrite_stack[-1]
        temp_id = self.rewrite_add[-1]
        del self.rewrite_stack[-1]
        del self.rewrite_add[-1]
        index = self.code.index(temp)
        self.code[index][3] = temp_id[1]
