# -*- coding: utf-8 -*-
# @Author : 吕澳辉
# @File : main.py
# @Software: PyCharm
# @version: python3.6

import argparse,os
from spylexer import Lexer
from spyparser import Parser
from runtime import RunTime

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-i','--input',help="input file")
    p.add_argument('-m', '--method',choices=['lexer','parser','run'])

    args = p.parse_args()
    infile = args.input
    method = args.method
    if infile==None or not os.path.exists(infile):
        infile = 'test/test.spy'
    if method==None or method not in ['lexer','parser']:
        method = 'run'
    with open(infile, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if method=="lexer":
        lexer = Lexer(lines)
        lexer.main()
        lexer.display()
    elif method=='parser':
        parser = Parser(lines)
        parser.main()
        parser.display(parser.tree.root,0)
    elif method=='run':
        parser = Parser(lines)
        parser.main()
        if parser.flag:
            runtime = RunTime(parser.tree.root)
            runtime.main()

if __name__ == '__main__':
    main()