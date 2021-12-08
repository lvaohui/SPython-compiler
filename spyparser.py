# -*- coding: utf-8 -*-
# @Author : 吕澳辉
# @File : spyparser.py
# @Software: PyCharm
# @version: python3.6

from spylexer import Lexer, keywords, types, operators
from error import print_traceback


class Node():
    '''语法树节点'''

    def __init__(self, value=None, _type=None, extra_info=None):
        self.value = value
        # token的类型
        self.type = _type
        # token的其他一些信息
        self.extra_info = extra_info
        self.father = None
        self.left = None
        self.right = None
        self.first_son = None


class Tree():
    '''语法树'''

    def __init__(self):
        # 根节点
        self.root = None
        # 现在的节点
        self.current = None

    def add_child_node(self, new_node, father=None):
        if not father:
            father = self.current
        new_node.father = father

        if not father.first_son:
            father.first_son = new_node
        else:
            current_node = father.first_son
            while current_node.right:
                current_node = current_node.right
            current_node.right = new_node
            new_node.left = current_node
        self.current = new_node


class Parser():
    '''语法分析器'''

    def __init__(self, lines):
        self.lines = lines
        lexer = Lexer(lines)
        lexer.main()
        self.flag = lexer.flag
        # 要分析的tokens
        self.tokens = lexer.tokens
        # tokens下标
        self.index = 0
        self.n = len(self.tokens)
        # 最终生成的语法树
        self.tree = Tree()


    # 声明语句
    def _statement(self, father=None):
        if not father:
            father = self.tree.root
        statement_tree = Tree()
        statement_tree.current = statement_tree.root = Node('Statement')
        self.tree.add_child_node(statement_tree.root, father)
        # 暂时用来保存当前声明语句的类型，以便于识别多个变量的声明
        tmp_variable_type = None
        while self.tokens[self.index].type != '\n':
            # 变量类型
            if self.tokens[self.index].value in types:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = Node('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    Node(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            # 变量名
            elif self.tokens[self.index].type == 'ID':
                # extra_info
                statement_tree.add_child_node(
                    Node(self.tokens[self.index].value, 'ID', {'type': 'VARIABLE', 'variable_type': tmp_variable_type}),
                    statement_tree.root)
            # 多个变量声明
            elif self.tokens[self.index].type == ',':
                while self.index < self.n and self.tokens[self.index].type != '\n':
                    if self.tokens[self.index].type == 'ID':
                        tree = Tree()
                        tree.current = tree.root = Node('Statement')
                        self.tree.add_child_node(tree.root, father)
                        # 类型
                        variable_type = Node('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        # 类型
                        tree.add_child_node(Node(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        # 变量名
                        tree.add_child_node(Node(self.tokens[self.index].value, 'IDENTIFIER', {
                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    # 函数声明
    def _function_statement(self, father=None):
        if not father:
            father = self.tree.root
        func_statement_tree = Tree()
        func_statement_tree.current = func_statement_tree.root = Node(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)
        # 函数声明语句什么时候结束
        flag = False
        func_statement_tree.add_child_node(Node('def'))
        type_node = Node('Type')
        func_statement_tree.add_child_node(type_node, func_statement_tree.root)
        self.index += 1
        while not flag and self.index < self.n:
            # 如果是函数返回类型
            if self.tokens[self.index].value == '<':
                if self.index + 1 < self.n and self.tokens[self.index + 1].value not in types:
                    print_traceback(self.lines, self.tokens[self.index].line_num, "函数定义语法错误")
                    self.flag = False
                    exit(0)
                if self.index + 2 < self.n and self.tokens[self.index + 2].value != '>':
                    print_traceback(self.lines, self.tokens[self.index].line_num, "函数定义语法错误")
                    self.flag = False
                    exit(0)
                func_statement_tree.add_child_node(
                    Node(self.tokens[self.index + 1].value, 'FIELD_TYPE', {'type': self.tokens[self.index + 1].value}),
                    type_node)
                self.index += 3
            # 如果是函数名
            elif self.tokens[self.index].type == 'ID':
                func_name = Node('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    Node(self.tokens[self.index].value, 'ID', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            # 如果是参数序列
            elif self.tokens[self.index].type == '(':
                params_list = Node('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.index < self.n and self.tokens[self.index].type != '\n' and self.tokens[
                    self.index].type != ')':
                    if self.tokens[self.index].value in types:
                        param = Node('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        func_statement_tree.add_child_node(Node('Type'), param)
                        # extra_info
                        func_statement_tree.add_child_node(
                            Node(self.tokens[self.index].value, 'FIELD_TYPE',
                                 {'type': self.tokens[self.index].value}), )
                        if self.index + 1 < self.n and self.tokens[self.index + 1].type == 'ID':
                            # extra_info
                            func_statement_tree.add_child_node(
                                Node(self.tokens[self.index + 1].value, 'ID', {
                                    'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                            if self.index + 2 < self.n and self.tokens[self.index + 2].type != ',' and \
                                    self.tokens[self.index + 2].type != ')':
                                print_traceback(self.lines, self.tokens[self.index].line_num, "函数定义语法错误")
                                self.flag = False
                                exit()
                        else:
                            print_traceback(self.lines, self.tokens[self.index].line_num, "函数定义语法错误")
                            self.flag = False
                            exit()
                        self.index += 1
                    self.index += 1
                if self.index == self.n or self.tokens[self.index] == '\n':
                    print_traceback(self.lines, self.tokens[self.index].line_num, "函数定义语法错误")
                    self.flag = False
                    exit()
                self.index += 1
            # 如果遇见冒号
            elif self.tokens[self.index].type == ':':
                if self.index + 1 < self.n and self.tokens[self.index + 1].type == '\n':
                    self.index += 1
                    self._sentence(func_statement_tree)
                else:
                    print_traceback(self.lines, self.tokens[self.index].line_num, "无函数体")
                    self.flag = False
                    exit()
                flag = True

    # 函数调用
    def _function_call(self, func_call_tree=None, father=None):
        if not func_call_tree:  # 表达式中的函数调用直接给出
            if not father:
                father = self.tree.root
            func_call_tree = Tree()
            func_call_tree.current = func_call_tree.root = Node('FunctionCall')
            self.tree.add_child_node(func_call_tree.root, father)
        while self.tokens[self.index].type != '\n' and self.tokens[self.index].type not in operators:
            # 函数名
            if self.tokens[self.index].type == 'ID':
                func_call_tree.add_child_node(
                    Node(self.tokens[self.index].value, 'FUNCTION_NAME'))
            # 左小括号
            elif self.tokens[self.index].type == '(':
                params_list = Node('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                # 右小括号位置
                tmp_index = self.index + 1
                arr = ['(']
                while tmp_index < self.n and self.tokens[tmp_index].type != '\n':
                    if self.tokens[tmp_index].type == '(':
                        arr.append('(')
                    elif self.tokens[tmp_index].type == ')':
                        arr.pop()
                    if not arr:
                        break
                    tmp_index += 1
                # if arr:
                #     print_traceback(self.lines,self.tokens[self.index].line_num,"括号不匹配")
                self.index += 1
                while self.index < tmp_index:
                    self._expression(params_list, tmp_index)
                    self.index += 1
                self.index = tmp_index + 1  # 调用后index在右括号的后一位
                return
            else:
                # print(self.tokens[self.index].value)
                print_traceback(self.lines, self.tokens[self.index].line_num, "函数调用错误")
                self.flag = False
                exit()
            self.index += 1
        # self.index += 1

    # 表达式
    def _expression(self, father=None, index=None):
        if not father:
            father = self.tree.root
            # 运算符优先级
        operator_priority = {'||': 0, '&&': 1, '!=': 2, '==': 2,
                             '>': 3, '<': 3, '>=': 3, '<=': 3,
                             '+': 4, '-': 4, '*': 5, '/': 5, }
        # 运算符栈
        operator_stack = []
        # 转换成的后缀表达式结果
        reverse_polish_expression = []
        # 中缀表达式转为后缀表达式，
        while self.index < self.n and self.tokens[self.index].type != '\n' and self.tokens[self.index].type != ',':
            # print(self.tokens[self.index].value)
            if index and self.index >= index:
                break
            # 如果是数字
            if self.tokens[self.index].type == 'NUMBER':
                tree = Tree()
                tree.current = tree.root = Node("Expression", 'NUMBER')
                tree.add_child_node(
                    Node(self.tokens[self.index].value, '_NUMBER'))
                reverse_polish_expression.append(tree)
                self.index += 1
            # 字符串
            elif self.tokens[self.index].type=='STRING':
                tree = Tree()
                tree.current = tree.root = Node("Expression", 'STRING')
                tree.add_child_node(
                    Node(self.tokens[self.index].value, '_STRING'))
                reverse_polish_expression.append(tree)
                self.index += 1
            # 如果是变量或者函数调用
            elif self.tokens[self.index].type == 'ID':
                # 变量
                if self.index+1==self.n or self.tokens[self.index + 1].value in operators or self.tokens[self.index + 1].type == '\n' or (
                        index and self.index + 1 == index):
                    tree = Tree()
                    tree.current = tree.root = Node(
                        "Expression", 'ID')
                    tree.add_child_node(
                        Node(self.tokens[self.index].value, '_ID'))
                    reverse_polish_expression.append(tree)
                    self.index += 1
                # 函数调用
                elif self.tokens[self.index + 1].type == '(':
                    tree = Tree()
                    tree.current = tree.root = Node(
                        'Expression', 'FunctionCall')
                    # 函数调用树
                    func_call_tree = Tree()
                    func_call_tree.current = func_call_tree.root = Node(
                        'FunctionCall', "_FunctionCall")
                    self._function_call(func_call_tree)
                    tree.add_child_node(func_call_tree.root)
                    reverse_polish_expression.append(tree)
                    # self.index -= 1
            # 如果是运算符
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == '(' or \
                    self.tokens[self.index].type == ')':
                tree = Tree()
                tree.current = tree.root = Node(
                    'Operator', 'Operator')
                tree.add_child_node(
                    Node(self.tokens[self.index].value, '_Operator'))
                # 如果是左括号，直接压栈
                if self.tokens[self.index].type == '(':
                    operator_stack.append(tree.root)
                # 如果是右括号，弹栈直到遇到左括号为止
                elif self.tokens[self.index].type == ')':
                    while operator_stack and operator_stack[-1].current.type != '(':
                        reverse_polish_expression.append(operator_stack.pop())
                    # 将左括号弹出来
                    if operator_stack:
                        operator_stack.pop()
                    else:
                        print_traceback(self.lines, self.tokens[self.index].line_num, "表达式括号不匹配")
                        self.flag = False
                        exit()
                # 其他只能是运算符
                else:
                    while operator_stack and operator_priority[tree.current.value] < operator_priority[
                        operator_stack[-1].current.value]:
                        reverse_polish_expression.append(operator_stack.pop())
                    operator_stack.append(tree)
                self.index += 1
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, "表达式无法解析")
                self.flag = False
                exit()
        # 最后将符号栈清空，最终得到后缀表达式reverse_polish_expression
        while operator_stack:
            reverse_polish_expression.append(operator_stack.pop())
        # 打印
        # for item in reverse_polish_expression:
        #   print(item.current.value,)
        # print

        # 操作数栈
        operand_stack = []
        child_operators = ['+', '-', '*', '/', '>', '<', '>=', '<=', '!=', '==', '||', '&&']
        for item in reverse_polish_expression:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            else:
                # 双目运算符
                if item.current.value in child_operators:
                    b = operand_stack.pop()
                    if not operand_stack:
                        a = Tree()
                        a.current = a.root = Node("Expression", 'NUMBER')
                        a.add_child_node(Node('0', '_NUMBER'))
                    else:
                        a = operand_stack.pop()
                    new_tree = Tree()
                    new_tree.current = new_tree.root = Node(
                        'Expression', 'DoubleOperand')
                    # 第一个操作数
                    new_tree.add_child_node(a.root)
                    # 操作符
                    new_tree.add_child_node(item.root, new_tree.root)
                    # 第二个操作数
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                else:
                    print_traceback(self.lines, self.tokens[self.index - 1].line_num, "运算符不支持")
                    self.flag = False
                    exit()
        self.tree.add_child_node(operand_stack[0].root, father)

    # 赋值语句
    def _assignment(self, father=None):
        if not father:
            father = self.tree.root
        assign_tree = Tree()
        assign_tree.current = assign_tree.root = Node('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        while self.index<self.n and self.tokens[self.index].type != '\n':
            # 被赋值的变量
            if self.tokens[self.index].type == 'ID':
                assign_tree.add_child_node(
                    Node(self.tokens[self.index].value, 'ID'))
                self.index += 1
            elif self.tokens[self.index].type == '=':
                assign_tree.add_child_node(Node('=', '='), assign_tree.root)
                self.index += 1
                self._expression(assign_tree.root)
        self.index += 1

    # if语句
    def _if_else(self, father=None):
        if_else_tree = Tree()
        if_else_tree.current = if_else_tree.root = Node(
            'IfElseControl', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = Tree()
        if_tree.current = if_tree.root = Node('IfControl')
        if_else_tree.add_child_node(if_tree.root)

        # if标志
        if self.tokens[self.index].type == 'if':
            self.index += 1
            tmp_index = self.index
            while self.tokens[tmp_index].type != ':':
                tmp_index += 1
            if tmp_index == self.index:
                print_traceback(self.lines, self.tokens[self.index].line_num, "if后无条件表达式")
                self.flag = False
                exit()
            self._expression(if_tree.root, tmp_index)
            if self.index + 1 < self.n and self.tokens[self.index + 1].type == '\n':
                self.index += 1
                self._sentence(if_tree)
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, "if条件后无执行语句")
                self.flag = False
                exit()

        # 如果有elif
        while self.tokens[self.index].type == 'elif':
            elif_tree = Tree()
            elif_tree.current = elif_tree.root = Node('ElifControl')
            if_else_tree.add_child_node(elif_tree.root, if_else_tree.root)
            self.index += 1
            tmp_index = self.index
            while self.tokens[tmp_index].type != ':':
                tmp_index += 1
            if tmp_index == self.index:
                print_traceback(self.lines, self.tokens[self.index].line_num, "elif后无条件表达式")
                self.flag = False
                exit()
            self._expression(elif_tree.root, tmp_index)
            if self.index + 1 < self.n and self.tokens[self.index + 1].type == '\n':
                self.index += 1
                self._sentence(elif_tree)
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, "elif条件后无执行语句")
                self.flag = False
                exit()
        # 如果是else
        if self.tokens[self.index].type == 'else':
            self.index += 1
            if self.tokens[self.index].type != ':':
                print_traceback(self.lines, self.tokens[self.index].line_num, "else语句语法错误")
                self.flag = False
                exit()
            else_tree = Tree()
            else_tree.current = else_tree.root = Node('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)
            if self.index + 1 < self.n and self.tokens[self.index + 1].type == '\n':
                self.index += 1
                self._sentence(else_tree)
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, "else条件后无执行语句")
                self.flag = False
                exit()

    # while语句，没处理do-while的情况，只处理了while
    def _while(self, father=None):
        while_tree = Tree()
        while_tree.current = while_tree.root = Node(
            'WhileControl', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)

        self.index += 1
        tmp_index = self.index
        while self.tokens[tmp_index].type != ':':
            tmp_index += 1
        if tmp_index == self.index:
            print_traceback(self.lines, self.tokens[self.index].line_num, "while后无条件表达式")
            self.flag = False
            exit()
        self._expression(while_tree.root, tmp_index)
        if self.index + 1 < self.n and self.tokens[self.index + 1].type == '\n':
            self.index += 1
            self._sentence(while_tree)
        else:
            print_traceback(self.lines, self.tokens[self.index].line_num, "while条件后无执行语句")
            self.flag = False
            exit()

    def _control(self, father=None):
        if  not father:
            father = self.tree.root
        token_type = self.tokens[self.index].type
        if token_type == 'if':
            self._if_else(father)
        elif token_type == 'while':
            self._while(father)
        else:
            print_traceback(self.lines, self.tokens[self.index].line_num, token_type + "无法单独出现")
            self.flag = False
            exit()

    # return语句
    def _return(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = Tree()
        return_tree.current = return_tree.root = Node('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.index<self.n and self.tokens[self.index].type != '\n':
            # 被赋值的变量
            if self.tokens[self.index].type == 'return':
                return_tree.add_child_node(
                    Node(self.tokens[self.index].value))
                self.index += 1
            else:
                self._expression(return_tree.root)
        self.index += 1

    # 判断句型
    def _judge_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # 声明
        if token_value in types:  # and self.tokens[self.index + 1].type == 'ID':
            if self.tokens[self.index + 1].type == 'ID':
                return 'STATEMENT'
            else:
                return '变量声明错误'
        # 函数调用或者赋值语句
        elif token_type == 'ID':
            index_1_token_type = self.tokens[self.index + 1].type
            if index_1_token_type == '(':
                return 'FUNCTION_CALL'
            elif index_1_token_type == '=':
                return 'ASSIGNMENT'
            else:
                return '语法错误'
        # 函数声明
        elif token_type == 'def':
            return 'FUNCTION_STATEMENT'
        elif token_type == 'return':
            return 'RETURN'
        elif token_value in keywords:
            return 'CONTROL'
        else:
            print(token_type)
            return '语法错误'

    # 语句块
    def _sentence(self, father_tree):
        father_deep = self.tokens[self.index].deep
        line_num = self.tokens[self.index].line_num
        self.index += 1
        sentence_tree = Tree()
        sentence_tree.current = sentence_tree.root = Node('Command')
        while self.index < self.n:
            if self.tokens[self.index].value == '\n':
                self.index += 1
                continue
            if self.tokens[self.index].deep <= father_deep:
                break
            if self.tokens[self.index].deep > father_deep + 1:
                print_traceback(self.lines, self.tokens[self.index].line_num, "缩进错误")
                self.flag = False
                exit()
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 声明语句
            if sentence_pattern == 'STATEMENT':
                self._statement(sentence_tree.root)
            # 赋值
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment(sentence_tree.root)
                pass
            # 函数声明
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement(sentence_tree.root)
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call(None, sentence_tree.root)
            elif sentence_pattern == 'CONTROL':
                self._control(sentence_tree.root)
            elif sentence_pattern == 'RETURN':
                self._return(sentence_tree.root)
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, sentence_pattern)
                self.flag = False
                exit()
        if not sentence_tree.root.first_son:
            print_traceback(self.lines, line_num, "语句块无语句")
            self.flag = False
            exit()
        father_tree.add_child_node(sentence_tree.root, father_tree.root)

    # 主程序
    def main(self):
        if not self.flag:
            return
        # 根节点
        self.tree.current = self.tree.root = Node('Command')
        while self.index < self.n:
            if self.tokens[self.index].value == '\n':
                self.index += 1
                continue
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 声明语句
            if sentence_pattern == 'STATEMENT':
                self._statement()
            # 函数声明语句
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
            # 赋值
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment()
            # 函数声明
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call()
            elif sentence_pattern == 'CONTROL':
                self._control()
            else:
                print_traceback(self.lines, self.tokens[self.index].line_num, sentence_pattern)
                self.flag = False
                return
        tree = Tree()
        tree.current = tree.root = Node('Program')
        tree.add_child_node(self.tree.root)
        self.tree.root = tree.root


    # 遍历语法树
    def display(self, node, idx):
        if not self.flag:
            return
        if not node:
            return
        if idx > 0:
            print('—' * 5, end='')
        child = node.first_son
        if child:
            print(node.value.center(19, '—'), end='')
            self.display(child, idx + 1)
            child = child.right
            while child:
                print()
                print(" " * (24 * (idx) + 9), end='')
                print("└" + "—" * 9, end='')
                self.display(child, idx + 1)
                child = child.right
        else:
            print(node.value.center(19, '—').rstrip('—'), end='')


if __name__ == '__main__':
    with open('test/test.spy', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    parser = Parser(lines)
    parser.main()
    parser.display(parser.tree.root,0)
