import copy
import graphviz
from generate_code import generate_code


class NODE():
    def __init__(self, element):
        self.ele = element
        self.children = []


class ast_tree():
    def __init__(self):
        self.root = NODE('#')
        self.p = self.root
        self.stack = [self.root]

    def add_node(self, element):
        node = NODE(element)
        self.p.children.append(node)
        self.stack.append(node)

    def pop_node(self):
        self.p = self.stack.pop()


class ll1_predict:
    def __init__(self, line='i'):
        fp = open('wenfa.txt', 'r', encoding='utf-8')
        self.data = fp.read()
        self.symbols = set()
        self.not_end = set()
        self.end = set()
        self.start = ''
        self.n = 1
        self.process_data()
        self.get_first()
        self.get_follow()
        self.create_table()
        self.analyse(line)
        if self.welldone == 1:
            self.print_ast_tree()

    # 数据处理
    def process_data(self):
        self.processed = []
        self.processed_left = []
        self.processed_right = []

        # 去除注释和空行
        self.data = self.data.split('\n')
        temp = [i for i in self.data if len(i) > 0]
        temp_2 = [i for i in temp if i[0] != '#']
        self.data = temp_2
        del temp
        del temp_2

        self.start = self.data[0].split('->')[0]
        for i in self.data:
            key, value = i.split('->')
            self.not_end.add(key)
            self.symbols.add(key)

            if '|' in value:
                value = value.split('|')
                for j in value:
                    self.data.append(key+'->'+j)
                continue

            value = value.split()
            for j in value:
                self.symbols.add(j)

            temp = [key, value]
            self.processed.append(temp)
            self.processed_left.append(key)
            self.processed_right.append(value)
        for i in self.symbols:
            if i not in self.not_end:
                self.end.add(i)

    def get_first(self):
        left = self.processed_left
        right = self.processed_right

        self.first = dict()
        self.first_from = dict()
        for i in self.not_end:
            self.first[i] = set()
            self.first_from[i] = dict()

        for i in range(len(right)):
            if right[i][0] in self.end:
                self.first_from[left[i]][right[i][0]] = right[i]
                self.first[left[i]].add(right[i][0])

        for dist in self.not_end:
            left_temp = [dist]
            left_temp_minus = []
            road = dict()
            change_flag = 1
            while change_flag == 1:
                temp_first = copy.deepcopy(self.first)
                change_flag = 0
                for i in range(len(right)):
                    temp = right[i][0]
                    if left[i] in left_temp or left[i] in left_temp_minus:
                        if temp in self.end:
                            if left[i] in left_temp_minus:
                                if temp == 'e':
                                    continue
                            if left[i] == dist:
                                self.first_from[dist][temp] = right[i]
                            else:
                                self.first_from[dist][temp] = road[left[i]]
                            self.first[dist].add(temp)
                        elif temp not in self.end:
                            flag = 0
                            for j in right[i]:
                                if j in self.end:
                                    if left[i] == dist:
                                        self.first_from[dist][j] = right[i]
                                    else:
                                        self.first_from[dist][j] = road[left[i]]
                                    self.first[dist].add(j)
                                    break
                                elif j in left_temp:
                                    flag = 1
                                    break
                                elif 'e' in self.first[j]:
                                    flag = 1
                                    # for k in self.first[j]:
                                    #     if k != 'e':
                                    #         if left[i] == dist:
                                    #             self.first_from[dist][k] = right[i]
                                    #         else:
                                    #             self.first_from[dist][k] = road[left[i]]
                                    #         self.first[dist].add(k)
                                    if j not in left_temp_minus:
                                        left_temp_minus.append(j)
                                        if left[i] != dist:
                                            road[j] = road[left[i]]
                                        else:
                                            road[j] = right[i]
                                        change_flag = 1
                                else:
                                    flag = 1
                                    left_temp.append(j)
                                    if left[i] != dist:
                                        road[j] = road[left[i]]
                                    else:
                                        road[j] = right[i]
                                    change_flag = 1
                                    break
                            if flag == 0:
                                if left[i] == dist:
                                    self.first_from[dist]['e'] = right[i]
                                else:
                                    self.first_from[dist]['e'] = road[left[i]]
                                self.first[dist].add('e')
                if temp_first != self.first:
                    change_flag = 1
        print('FIRST')
        for i in self.not_end:
            print(i, end='->')
            for j in self.first[i]:
                print(j, end=' ')
            print()

    def get_follow(self):
        left = self.processed_left
        right = self.processed_right

        self.follow = dict()
        for i in self.not_end:
            self.follow[i] = set()
        self.follow[self.start].add('#')

        for dist_2 in self.not_end:
            change_flag = 1
            left_temp = [dist_2]
            while change_flag == 1:
                change_flag = 0
                temp_follow = copy.deepcopy(self.follow)
                for i in range(len(right)):
                    temp = right[i]
                    for dist in left_temp:
                        if left[i] != dist and dist in temp:
                            index_dist = temp.index(dist)
                            if index_dist == len(temp) - 1:
                                if left[i] not in left_temp:
                                    left_temp.append(left[i])
                                    change_flag = 1
                            else:
                                add_flag = 1
                                for j in range(index_dist+1, len(temp)):
                                    if temp[j] in self.end:
                                        self.follow[dist] |= set(temp[j])
                                        add_flag = 0
                                        break
                                    elif 'e' in self.first[temp[j]]:
                                        self.follow[dist] |= self.first[temp[j]]
                                        self.follow[dist] -= set('e')
                                        continue
                                    else:
                                        self.follow[dist] |= self.first[temp[j]]
                                        self.follow[dist] -= set('e')
                                        add_flag = 0
                                if add_flag == 1:
                                    if left[i] not in left_temp:
                                        left_temp.append(left[i])
                                        change_flag = 1
                if temp_follow != self.follow:
                    change_flag = 1
            for i in left_temp:
                self.follow[dist_2] |= self.follow[i]
        print('FOLLOW')
        for i in self.not_end:
            print(i, end='->')
            for j in self.follow[i]:
                print(j, end=' ')
            print()
        print()

    def create_table(self):
        self.table = dict()
        for i in self.not_end:
            self.table[i] = dict()
        for i in self.not_end:
            for j in self.end:
                if j == 'e':
                    continue
                self.table[i][j] = 'ERROR'
            self.table[i]['#'] = 'ERROR'

        for i in self.not_end:
            for j in self.first[i]:
                if j == 'e':
                    for k in self.follow[i]:
                        self.table[i][k] = ['e']
                    continue
                self.table[i][j] = self.first_from[i][j]

    def analyse(self, line):
        self.ast = ast_tree()
        stack = ['#', self.start]
        line.append(['', '#'])
        p = 0
        top = stack.pop()
        record = ''
        cur_char = line[p][1]

        while top != '#':
            if top in self.end and top == cur_char:
                record += str(stack) + ' ' + cur_char + '匹配成功\n'
                print(str(stack) + ' ' + cur_char + '匹配成功')
                if cur_char in ['identifier', 'number']:
                    cur_id = line[p][0]
                    self.ast.p.ele = [self.ast.p.ele]
                    self.ast.p.ele.append(cur_id)
                p += 1
                cur_char = line[p][1]
            elif top in self.not_end and cur_char in self.table[top] and self.table[top][cur_char] != 'ERROR':
                record += str(stack) + ' ' + top + '->' + \
                    str(self.table[top][cur_char]) + '\n'
                print(str(stack) + ' ' + top + '->' +
                      str(self.table[top][cur_char]))
                temp = self.table[top][cur_char]
                for char in reversed(temp):
                    if char != 'e':
                        self.ast.add_node(char)
                        stack.append(char)
            else:
                break

            self.ast.pop_node()
            top = stack.pop()
        if top == cur_char:
            record += '接受\n'
            print('接受')
            self.welldone = 1
        else:
            record += '匹配失败\n'
            print('匹配失败')
            self.welldone = 0
        # print(record)

    def print_tree(self, f, ast_node, father):
        if len(ast_node.children) == 0:
            return
        else:
            for i in reversed(ast_node.children):
                if isinstance(i.ele, list):
                    f.node(str(self.n), fontname='Microsoft YaHei',
                           label=i.ele[0]+':'+i.ele[1])
                else:
                    f.node(str(self.n), fontname='Microsoft YaHei',
                           label=i.ele)
                f.edge(str(father), str(self.n))
                self.n += 1
                self.print_tree(f, i, self.n-1)

    def print_ast_tree(self):
        f = graphviz.Digraph('NFA', format='png',
                             filename='D:/Softwares/Python/ast_tree')
        f.node(str(0), fontname='Microsoft YaHei', label='#')
        self.print_tree(f, self.ast.root, 0)
        f.render(view=True)


if __name__ == '__main__':
    ll1 = ll1_predict()
    print()
