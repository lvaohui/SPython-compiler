# -*- coding: utf-8 -*-
# @Author : 吕澳辉
# @File : spylexer.py
# @Software: PyCharm
# @version: python3.6

from error import print_traceback

# 运算符表
operators = {"+", "-", "*", "/", "=", "<","<=", ">", ">=", "==","!=" ,",","&&", "||"}

# 分隔符表
separators = {":",'\n'}
# 关键字表
keywords = {
    "if","else","elif","while","def","return"
}
# 类型
types = {"int", "float", "char", "string","bool"}
# 括号配对
kuo = {'(': ')'}

# 得到代码行的深度
# 判断代码所属的块
def get_line_deep(line):
    deep = 0
    for s in line:
        if s!=' ':
            if deep % 4==0:
                return int(deep/4)
            return -1
        deep += 1


# 得到单或双引号中的内容，返回i
def jump_to_next(line,i,ch):
    n = len(line)
    while i < n and line[i] != ch:
        if line[i] == '\\':
            i += 1
        i += 1
    return i


class Token():
    def __init__(self, type, value,line_num,deep):
        self.type=type
        self.value=value
        self.line_num=line_num
        self.deep = deep


class Lexer():
    def __init__(self, lines):
        self.tokens = []  # 输出单词列表
        self.flag = True  # 源代码是否正确标识
        self.lines = lines

    # 分词主函数
    def main(self):
        kuo_list = []  # 存储括号并判断是否完整匹配
        line_num = 0
        for line in self.lines:
            line_num += 1
            deep = get_line_deep(line)
            if deep==-1:
                print_traceback(self.lines, line_num, "代码缩进错误")
                self.flag = False
                return
            line = line.lstrip()
            n = len(line)
            i = 0
            while i < n:
                # 字符串
                if line[i] == '"':
                    st = i + 1
                    i = jump_to_next(line,st,'"')
                    if i>=n:# 无法找到匹配的双引号，错误
                        print_traceback(self.lines,line_num,"双引号无法匹配")
                        self.flag = False
                        return
                    self.tokens.append(Token('STRING',line[st:i],line_num,deep))
                    i += 1
                # 字符
                elif line[i] == "'":
                    st = i + 1
                    i = jump_to_next(line, st, "'")
                    if i>=n:# 无法找到匹配的单引号，错误
                        print_traceback(self.lines,line_num,"单引号无法匹配")
                        self.flag = False
                        return
                    if (i-st==1 and line[st:i]=='\\') or (i-st==2 and line[st:st+1]!='\\' ) or (i-st>2):
                        print_traceback(self.lines, line_num, "单引号中类型错误")
                        self.flag = False
                        return
                    self.tokens.append(Token('CHAR',line[st:i],line_num,deep))
                    i += 1
                # 运算符
                elif line[i] in operators:
                    st = i
                    i += 1
                    while line[st:i] in operators and i <= n:
                        i += 1
                    i -= 1
                    op = line[st:i]
                    self.tokens.append(Token(op,op,line_num,deep))
                elif line[i:i+2] in operators:
                    self.tokens.append(Token(line[i:i+2],line[i:i+2],line_num,deep))
                    i+=2
                # 分隔符，冒号,分号
                elif line[i] in separators:
                    self.tokens.append(Token(line[i],line[i],line_num,deep))
                    i+=1
                # 数字
                elif line[i].isdigit():
                    st = i
                    i += 1
                    while i < n and (line[i].isdigit() or line[i]=='.'):
                        i += 1
                    num = line[st:i]
                    if i<n and ( line[i].isalpha() or line[i]=='_'):# 数字后紧跟字符
                        print_traceback(self.lines, line_num, "变量名称不合法")
                        self.flag = False
                        return
                    if num.rfind('.') != num.find('.'): # 小数不合法
                        print_traceback(self.lines,line_num,"小数类型不合法")
                        self.flag = False
                        return
                    self.tokens.append(Token('NUMBER',num,line_num,deep))
                # 括号
                elif line[i] in kuo.values() or line[i] in kuo.keys():
                    # 左括号入栈
                    if line[i] in kuo.keys():
                        kuo_list.append(line[i])
                        # 右括号判断是否匹配并出栈
                    elif kuo_list and line[i] == kuo[kuo_list[-1]]:
                        kuo_list.pop()
                    else:
                        print_traceback(self.lines,line_num,"括号无法匹配")
                        self.flag = False
                        return
                    self.tokens.append(Token(line[i],line[i],line_num,deep))
                    i+=1
                # 跳过空格
                elif line[i]==' ':
                    i+=1
                # 自定义名称
                else:
                    st = i
                    while i < n and (line[i] == '_' or line[i].isdigit() or line[i].isalpha()):
                        i += 1
                    if i==st:
                        print_traceback(self.lines, line_num, "变量名称不合法")
                        self.flag = False
                        return
                    w = line[st:i]
                    if w in keywords: # 关键词
                        self.tokens.append(Token(w,w,line_num,deep))
                    elif w in types: #变量类型
                        self.tokens.append(Token(w,w,line_num,deep))
                    else:#自定义的变量名称
                        self.tokens.append(Token('ID',w,line_num,deep))
                # print(line,i,line[i])
            if kuo_list:
                print_traceback(self.lines, line_num, "括号无法闭合")
                self.flag = False
                return

    def display(self):
        if not self.flag:
            return
        for token in self.tokens:
            print((token.type,token.value))



if __name__ == '__main__':
    filename = 'test/test.spy'
    with open(filename,'r',encoding='utf-8') as f:
        lines = f.readlines()
    lex = Lexer(lines)
    lex.main()
    lex.display()
