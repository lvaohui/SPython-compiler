# -*- coding: utf-8 -*-
# @Author : 吕澳辉
# @File : error.py
# @Software: PyCharm
# @version: python3.6

def print_traceback(lines,err_line_num,err_msg):
    print(f"Traceback:\tline {err_line_num}")
    err_num = err_line_num -1 #行下标
    st = 0 if err_num-2<0 else err_num-2
    ed = len(lines) if err_num+2>len(lines) else err_num + 2
    for i in range(st,ed):
        print("  %4d|%s" % (i+1,lines[i].rstrip()))
    print(f"Error: {err_msg}")