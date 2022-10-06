import ply.lex as lex

error_list = ''

reserved = {
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'goto': 'GOTO',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'unsigned': 'UNSIGNED',
    'int': 'INT',
    'char': 'CHAR',
    'float': 'FLOAT',
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'return': 'RETURN',
    'void': 'VOID',
    'main': 'MAIN',
    # add more...
}

tokens = [
    'PLUS',  # +
    'PLUS1',  # ++
    'MINUS',  # -
    'MINUS1',  # --
    'TIMES',  # *
    'TIMES_EQUAL',  # *=
    'DIVIDE',  # /
    'DIVIDE_EQUAL',  # /=
    'GT',  # >
    'LT',  # <
    'GE',  # >=
    'LE',  # <=
    'EQUAL',  # ==
    'NEQUAL',  # !=
    'SEMI',  # ;
    'COMMA',  # ,
    'ASSIGN',  # =
    'LPAREN',  # (
    'RPAREN',  # )
    'LBRACKET',  # [
    'RBRACKET',  # ]
    'LBRACE',  # {
    'RBRACE',  # }
    'SHARP',
    'AND',  # &
    'OR',  # |
    'POINT',  # .
    'REM',  # %
    'ID',  # 标识符
    'NUM',  # 整数
    'HEX',  # 十六进制
    'OCT',  # 八进制
    'STR',  # 字符串
    'IEEE754',
    'FNUM',
] + list(reserved.values())


def ply_lexer():
    digit = r'([0-9])'
    letter = r'([_A-Za-z])'
    identifier = r'(' + letter + r'(' + digit + r'|' + letter + r')*)'
    number = r' 0 | [1-9]\d* '

    t_PLUS = r'\+'
    t_PLUS1 = r'\+\+'
    t_MINUS = r'-'
    t_MINUS1 = r'--'
    t_TIMES = r'\*'
    t_TIMES_EQUAL = r'\*\='
    t_DIVIDE = r'/'
    t_DIVIDE_EQUAL = r'/\='
    t_LT = r'\<'
    t_LE = r'\<\='
    t_GT = r'\>'
    t_GE = r'\>\='
    t_EQUAL = r'\=\='
    t_NEQUAL = r'\!\='
    t_ASSIGN = r'\='
    t_SEMI = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SHARP = r'\#'
    t_REM = r'%'
    t_AND = r'&'
    t_OR = r'\|'
    t_POINT = r'\.'

    t_STR = r'(\' .* \') | (\" .* \")'

    def t_IEEE754(t):
        r'([1-9] \d* . \d+ [Ee] \d* [+-] \d+) | ([1-9] \d* [Ee] ( (\d+) | ([+-] \d+)) )'
        return t

    def t_ID_ERROR(t):
        r'[1-9]+ [a-zA-Z]+'
        print('error ID at %d' % t.lexer.lineno)
        global error_list
        error_list += 'error ID at line ' + str(t.lexer.lineno) + '\n'

    def t_FNUM_ERROR(t):
        r'([1-9] \d* \. \d+ \. \d*)'
        print('error ID at %d' % t.lexer.lineno)
        global error_list
        error_list += 'error NUM at line ' + str(t.lexer.lineno) + '\n'

    def t_FNUM(t):
        r'[1-9] \d* \. \d+'
        return t

    def t_OCT_ERROR(t):
        r'(0 [0-7]* [8-9]+ [0-7]*) | (0 0+ [0-7]*) '
        print('error OCT at %d' % t.lexer.lineno)
        global error_list
        error_list += 'error OCT at line ' + str(t.lexer.lineno) + '\n'

    def t_OCT(t):
        r'0 [0-7]+'
        return t

    def t_HEX_ERROR(t):
        r'0 [xX] [0-9]* [g-zG-Z]+ [0-9]* '
        print('error HEX at %d' % t.lexer.lineno)
        global error_list
        error_list += 'error HEX at line ' + str(t.lexer.lineno) + '\n'

    def t_HEX(t):
        r'0 [xX] ([0-9] | [A-Fa-f])+ '
        return t

    def t_NUM(t):
        t.value = int(t.value)
        return t

    t_NUM.__doc__ = number

    def t_ID(t):
        t.type = reserved.get(t.value, 'ID')    # Check for reserved words
        # Look up symbol table information and return a tuple
        # t.value = (t.value, symbol_lookup(t.value))
        return t

    t_ID.__doc__ = identifier

    # C-style comment (/* ... */)
    def t_comment(t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    # C++-style comment (//...)
    def t_cpp_comment(t):
        r'//.*\n'
        t.lexer.lineno += 1

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(t):
        global error_list
        print("Illegal character '%s'" % t.value[0])
        error_list += 'Illegal character ' + \
            t.value[0] + ' at line ' + str(t.lexer.lineno) + '\n'
        t.lexer.skip(1)

    # Build the lexer
    lexer = lex.lex()
    return lexer


def open_file(path):
    global error_list

    error_list = ''
    lexer = ply_lexer()
    data = open(path, 'r', encoding='utf-8-sig').read()
    lexer.input(data)
    result = []
    while True:
        token = lexer.token()
        if not token:
            break
        temp = []
        temp.append(str(token.value))
        temp.append(token.type)
        temp.append(str(token.lineno))
        result.append(temp)
        print(str(token.value) + '\t\t' +
              token.type + '\t\t' + str(token.lineno))
    return result, error_list


if __name__ == '__main__':
    lexer = ply_lexer()
    data = open('source.txt', 'r', encoding='utf-8-sig').read()
    lexer.input(data)

    while True:
        token = lexer.token()
        if not token:
            break
        print(str(token.value) + '\t\t' +
              token.type + '\t\t' + str(token.lineno))
