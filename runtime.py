# -*- coding: utf-8 -*-
# @Author : 吕澳辉
# @File : runtime.py
# @Software: PyCharm
# @version: python3.6

from spyparser import Parser,Tree,Node
from queue import Queue


class RunTime():
    def __init__(self,root=None):
        self.root = root
        self.id = {}
        self.function = {}

    def initStateParameter(self,node,value_list):
        cur = node.first_son
        i = 0
        while cur:
            self.id[cur.first_son.right.value]={
                'type':cur.first_son.first_son.value,
                'value':value_list[i]
            }
            i += 1
            cur = cur.right

    def call_function(self,fun):
        name = fun.first_son.value
        parameter_epxr = []
        parameter = fun.first_son.right
        cur = parameter.first_son
        while cur:
            parameter_epxr.append(cur)
            cur = cur.right
        parameter_value = []
        for p in parameter_epxr:
            parameter_value.append(self.expr_value(p))
        if name=='print':
            print(" ".join(str(item) for item in parameter_value))
        else:
            node = self.function[name]
            StateParameterList = node.first_son.right.right.right
            fun_runtime = RunTime(StateParameterList.right)
            fun_runtime.function[name] = node # 添加自己，可以递归
            fun_runtime.initStateParameter(StateParameterList,parameter_value)
            return fun_runtime.main()


    def expr_value(self,node=Node()):
        if node.type=='NUMBER':
            return int(node.first_son.value)
        if node.type=='STRING':
            return node.first_son.value
        if node.type=='ID':
            return self.id[node.first_son.value]['value']
        if node.type=='DoubleOperand':
            a = self.expr_value(node.first_son)
            a = f'"{a}"' if type(a)==str else a
            op = node.first_son.right
            b = self.expr_value(op.right)
            b = f'"{b}"' if type(b)==str else b
            op = op.first_son.value
            if op=='/':
                op = '//'
            return eval(f"{a}{op}{b}")
        if node.type=='FunctionCall':
            fun = node.first_son
            return self.call_function(fun)

    def main(self,root=None):
        queue = Queue()
        if not root:
            queue.put(self.root)
        else:
            queue.put(root)
        while not queue.empty():
            node = queue.get()
            if node.value == 'FunctionStatement':
                self.function[node.first_son.right.right.first_son.value] = node
            elif node.value == 'Statement':
                self.id[node.first_son.right.value] = {
                    'type': node.first_son.first_son.value,
                    'value': None
                }
            elif node.value == 'Assignment':
                self.id[node.first_son.value]['value'] = self.expr_value(node.first_son.right.right)
            elif node.value == 'FunctionCall':
                self.call_function(node)
            elif node.value=='Return':
                return self.expr_value(node.first_son.right)
            elif node.value=='IfElseControl':
                ifc = node.first_son
                exp = self.expr_value(ifc.first_son)
                if exp:
                    ret =self.main(ifc.first_son.right)
                    if ret and ret=='normal':
                        pass
                    else:
                        return ret
                else:
                    elc = ifc.right
                    while elc:
                        if elc.value=='ElseControl':
                            ret = self.main(elc.first_son)
                            if ret and ret == 'normal':
                                pass
                            else:
                                return ret
                            break
                        else:
                            exp = self.expr_value(elc.first_son)
                            if exp:
                                ret = self.main(elc.first_son.right)
                                if ret and ret == 'normal':
                                    pass
                                else:
                                    return ret
                                break
                            elc = elc.right
            elif node.value=='WhileControl':
                while self.expr_value(node.first_son):
                    ret = self.main(node.first_son.right)
                    if ret and ret=='normal':
                        pass
                    else:
                        return ret
            elif node.first_son:
                queue.put(node.first_son)
            if node.right:
                queue.put(node.right)
        return "normal"


if __name__ == '__main__':
    with open('test/test.spy', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    parser = Parser(lines)
    parser.main()
    if parser.flag:
        runtime = RunTime(parser.tree.root)
        runtime.main()
    pass