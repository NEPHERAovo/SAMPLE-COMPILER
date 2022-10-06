import graphviz


def epsilon():
    return 'ε'


class Automata:
    '''生成自动机的类'''

    def __init__(self, language=set()):
        self.states = set()
        self.start_state = None
        self.final_states = []
        self.edges = dict()
        self.language = language

    # 设置开始节点
    def set_start_state(self, state):
        self.start_state = state
        self.states.add(state)

    # 设置终点(s)
    def add_final_states(self, state):
        if isinstance(state, int):
            state = [state]
        for t in state:
            # DFA不加这个喜提n个重复终点
            if t not in self.final_states:
                self.final_states.append(t)

    # 添加边
    def add_edge(self, from_state, to_state, inp):
        self.states.add(from_state)
        self.states.add(to_state)
        if from_state in self.edges:
            # 路线存在
            if to_state in self.edges[from_state]:
                # 取记号并集
                if self.edges[from_state][to_state] != inp:
                    self.edges[from_state][to_state] += ',' + inp
            else:
                self.edges[from_state][to_state] = inp
        else:
            self.edges[from_state] = {to_state: inp}

    def add_edges(self, lines):
        # non-iterable type 需要 .items()
        for from_state, to_states in lines.items():
            for state in to_states:
                self.add_edge(from_state, state, to_states[state])

    def new_build(self, start):
        translations = dict()
        for i in list(self.states):
            translations[i] = start
            start += 1
        re_mata = Automata()
        # 原起点终点标号更新
        re_mata.set_start_state(translations[self.start_state])
        re_mata.add_final_states(translations[self.final_states[0]])
        for from_state, to_states in self.edges.items():
            for state in to_states:
                re_mata.add_edge(
                    translations[from_state], translations[state], to_states[state])
        return [re_mata, start]

    # get epsilon closure
    def get_eclosure(self, states_target):
        if isinstance(states_target, int):
            states_target = [states_target]
        states_all = set()
        states = set(states_target)
        while len(states) != 0:
            state = states.pop()
            states_all.add(state)
            if state in self.edges:
                for target in self.edges[state]:
                    if epsilon() in self.edges[state][target] and target not in states_all:
                        states.add(target)
        return states_all

    # 求出 move()
    def get_edge(self, state, inp):
        if isinstance(state, int):
            state = [state]
        states = set()
        for st in state:
            if st in self.edges:
                for target in self.edges[st]:
                    if inp in self.edges[st][target]:
                        states.add(target)
        return states

    # 展示（debug用
    def display(self):
        print("states:", self.states)
        print("start state: ", self.start_state)
        print("final states:", self.final_states)
        print("transitions:")
        for from_state, to_states in self.edges.items():
            for state in to_states:
                print("  ", from_state, "->", state,
                      "  char '"+to_states[state]+"'",)

    # 画图（使用graphviz
    def draw_automafa(self, name):
        f = graphviz.Digraph('NFA', format='png',
                             filename='D:/Softwares/Python/'+name)
        f.graph_attr['rankdir'] = 'LR'
        f.attr('node', shape='plaintext')
        f.node('start')
        f.attr('node', shape='doublecircle')
        for node in self.states:
            if node in self.final_states:
                f.node(str(node))
        f.attr('node', shape='circle')
        for from_state, to_states in self.edges.items():
            for state in to_states:
                f.edge(str(from_state), str(state), label=to_states[state])
        if name == 'nfa':
            f.edge('start', str(0))
        else:
            f.edge('start', 'A')
        f.render()


class DFA2MDFA:
    def __init__(self, dfa_object):
        self.dfa = dfa_object.dfa
        self.build_MDFA()

    # 将 A 结点改为 B 结点
    def switch_node(self, nodeA, nodeB, dict):
        for i in dict:
            if nodeA in dict[i]:
                if nodeB in dict[i]:
                    if dict[i][nodeB] != dict[i][nodeA]:
                        dict[i][nodeB] += ','+dict[i][nodeA]
                    del dict[i][nodeA]
                else:
                    dict[i][nodeB] = dict[i].pop(nodeA)
        return dict

    # 删除结点
    def del_node(self, nodes, to_node):
        # A 结点初始不变
        for i in range(len(nodes)):
            if nodes[i] == 'A':
                nodes[i] = to_node
                to_node = 'A'

        temp = {}
        for key, value in self.dfa.edges.items():
            temp[key] = value

        del_number = -1
        for node in nodes:
            del_number += 1
            node = chr(ord(node)-del_number)
            if node in temp:
                # 删除该结点
                del temp[node]
                self.dfa.states.remove(node)
                if node in self.dfa.final_states:
                    self.dfa.final_states.remove(node)
                # 路径修改
                temp = self.switch_node(node, to_node, temp)
                # 后续结点前移
                for i in range(len(temp)+1):
                    j = i + ord('A')
                    if j > ord(node):
                        temp[chr(j-1)] = temp.pop(chr(j))
                        temp = self.switch_node(chr(j), chr(j - 1), temp)
                        self.dfa.states.remove(chr(j))
                        self.dfa.states.add(chr(j-1))
                        if chr(j) in self.dfa.final_states:
                            self.dfa.final_states.remove(chr(j))
                            self.dfa.final_states.append(chr(j-1))
        self.dfa.edges.clear()
        for key, value in temp.items():
            self.dfa.edges[key] = value

    def build_MDFA(self):
        not_end_list = list((self.dfa.states) - set(self.dfa.final_states))
        end_list = self.dfa.final_states
        edge_dic = {}
        while len(not_end_list) > 1:
            # 每次删除后更新list
            not_end_list = list((self.dfa.states) - set(self.dfa.final_states))
            edge_dic.clear()
            for i in not_end_list:
                edge_dic[i] = self.dfa.edges[i]
            temp = []
            for key, value in edge_dic.items():
                temp.append([key, value])

            del_flag = 0
            for i in temp:
                del_flag = 0
                del_nodes = []
                # 找到与该点可到达路径相同的点
                for j in range(temp.index(i)+1, len(temp)):
                    if temp[j][1] == i[1]:
                        del_nodes.append(temp[j][0])
                        # 只保留该点
                        to_node = i[0]
                        del_flag = 1
                if del_flag == 1:
                    self.del_node(del_nodes, to_node)
                    break
            if del_flag == 0:
                break

        # 终结符
        while len(end_list) > 1:
            end_list = self.dfa.final_states
            edge_dic.clear()
            tempflag = 0
            for i in end_list:
                if i not in self.dfa.edges:
                    tempflag = 1
                    break
                edge_dic[i] = self.dfa.edges[i]
            if tempflag == 1:
                break
            temp = []
            for key, value in edge_dic.items():
                temp.append([key, value])

            for i in temp:
                del_flag = 0
                del_nodes = []
                for j in range(temp.index(i)+1, len(temp)):
                    if temp[j][1] == i[1]:
                        del_nodes.append(temp[j][0])
                        to_node = i[0]
                        del_flag = 1
                if del_flag == 1:
                    self.del_node(del_nodes, to_node)
                    break
            if del_flag == 0:
                break

        self.mdfa = self.dfa
        self.mdfa.display()
        self.mdfa.draw_automafa('mdfa')


class NFA2DFA:
    def __init__(self, nfa_object):
        self.nfa = nfa_object.nfa
        # DFA中用大写字母表示状态
        self.alphabet = [chr(i) for i in range(65, 91)]
        self.build_DFA()

    def build_DFA(self):
        all_states = dict()
        e_closure = dict()
        count = 0
        # 得到开始状态的e_closure
        state1 = self.nfa.get_eclosure(self.nfa.start_state)
        e_closure[self.nfa.start_state] = state1
        # 初始化dfa，添加初始状态
        dfa = Automata(self.nfa.language)
        dfa.set_start_state(self.alphabet[count])
        states = [[state1, count]]
        all_states[count] = state1
        count += 1

        # 当包含未标记的状态
        while len(states) != 0:
            [state, from_index] = states.pop()
            from_index = self.alphabet[from_index]
            for char in dfa.language:
                target = self.nfa.get_edge(state, char)
                for s in target:
                    if s not in e_closure:
                        e_closure[s] = self.nfa.get_eclosure(s)
                    target = target.union(e_closure[s])
                if len(target) != 0:
                    # 转换闭包不存在则添加
                    if target not in all_states.values():
                        states.append([target, count])
                        all_states[count] = target
                        to_index = self.alphabet[count]
                        count += 1
                    # 否则找到已添加中的对应状态
                    else:
                        to_index = [k for k, v in all_states.items()
                                    if v == target][0]
                        to_index = self.alphabet[to_index]
                    dfa.add_edge(from_index, to_index, char)
        for value, state in all_states.items():
            # 如果可以到终点
            if self.nfa.final_states[0] in state:
                dfa.add_final_states(self.alphabet[value])
        self.dfa = dfa
        self.dfa.display()
        self.dfa.draw_automafa('dfa')


class Regex2NFA:
    def __init__(self, regex):
        self.regex = regex
        # 合法字符(们)
        self.alphabet = [chr(i) for i in range(65, 91)]
        self.alphabet.extend([chr(i) for i in range(97, 123)])
        self.alphabet.extend([chr(i) for i in range(48, 58)])
        self.alphabet.extend(epsilon())
        self.build_NFA()

    '''操作部分'''
    '''建立新的自动机'''
    '''加上不同操作需要的弧'''
    '''再将原来自动机的弧添加进来'''

    # ab
    def base_operator(self, inp):
        base = Automata()
        base.set_start_state(0)
        base.add_final_states(1)
        base.add_edge(0, 1, inp)
        return base

    # a.b（连接
    def dot_operator(self, a, b):
        [a, m] = a.new_build(0)
        [b, n] = b.new_build(m-1)
        dot = Automata()
        dot.set_start_state(0)
        dot.add_final_states(n-1)
        dot.add_edges(a.edges)
        dot.add_edges(b.edges)
        return dot

    # a*
    def star_operator(self, a):
        [a, n] = a.new_build(1)
        star = Automata()
        star.set_start_state(0)
        star.add_final_states(n)
        star.add_edge(0, a.start_state, epsilon())
        star.add_edge(0, n, epsilon())
        star.add_edge(a.final_states[0], n, epsilon())
        star.add_edge(a.final_states[0], a.start_state, epsilon())
        star.add_edges(a.edges)
        return star

    # a|b
    def or_operator(self, a, b):
        [a, m] = a.new_build(1)
        [b, n] = b.new_build(m)
        orr = Automata()
        orr.set_start_state(0)
        orr.add_final_states(n)
        orr.add_edge(0, a.start_state, epsilon())
        orr.add_edge(0, b.start_state, epsilon())
        orr.add_edge(a.final_states[0], n, epsilon())
        orr.add_edge(b.final_states[0], n, epsilon())
        orr.add_edges(a.edges)
        orr.add_edges(b.edges)
        return orr

    '''构建NFA部分'''
    # 操作符入栈

    def add_operator(self, char):
        while True:
            if len(self.stack) == 0:
                break
            top = self.stack[-1]
            if top == '(':
                break
            if top == char or top == '.':
                self.process_operator(self.stack.pop())
            else:
                break
        self.stack.append(char)

    # 处理操作符
    def process_operator(self, op):
        if op == '*':
            self.automata.append(self.star_operator(self.automata.pop()))
        elif op == '|':
            a = self.automata.pop()
            b = self.automata.pop()
            self.automata.append(self.or_operator(b, a))
        elif op == '.':
            a = self.automata.pop()
            b = self.automata.pop()
            self.automata.append(self.dot_operator(b, a))

    def build_NFA(self):
        language = set()
        prev = None
        self.stack = []
        self.automata = []
        for char in self.regex:

            if char in self.alphabet:
                language.add(char)
                if prev != '.' and (prev in self.alphabet or prev in [')', '*']):
                    # 添加点用于分隔
                    self.add_operator('.')
                self.automata.append(self.base_operator(char))

            elif char == '(':
                if prev != '.' and (prev in self.alphabet or prev in [')', '*']):
                    self.add_operator('.')
                # 左括号入栈
                self.stack.append(char)

            elif char == ')':
                while True:
                    top = self.stack.pop()
                    # 找到对应左括号为止
                    if top == '(':
                        break
                    # 处理操作符
                    elif top in ['|', '.']:
                        self.process_operator(top)
            # |入栈
            elif char == '|':
                self.add_operator(char)

            # *直接处理
            elif char == '*':
                self.process_operator('*')
            prev = char

        while len(self.stack) != 0:
            op = self.stack.pop()
            self.process_operator(op)

        self.nfa = self.automata.pop()
        self.nfa.language = language
        print('regex = ' + self.regex)
        self.nfa.display()
        self.nfa.draw_automafa('nfa')


class gui_display:
    def __init__(self, reg):
        self.regex = reg

    def regex_nfa(self):
        self.nfa_object = Regex2NFA(self.regex)

    def nfa_dfa(self):
        self.dfa_object = NFA2DFA(self.nfa_object)

    def dfa_mdfa(self):
        self.mdfa_object = DFA2MDFA(self.dfa_object)


if __name__ == '__main__':
    nfa_object = Regex2NFA('(a|b)*abb(a|b)*')
    dfa_object = NFA2DFA(nfa_object)
    mdfa_object = DFA2MDFA(dfa_object)
