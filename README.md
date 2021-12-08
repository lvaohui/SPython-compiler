
# SPython语言

## 源代码说明
+ spylexer.py为词法分析器

+ spyparser.py为语法分析器

+ error.py中有报错输出函数

+ runtime.py为使用python模拟的运行环境

+ main.py主函数入口

## 使用

```shell script
# 指定代码文件为test/test.spy,运行代码
python main.py -i test/test.spy -m run 

# 进行词法分析输出结果
python main.py -i test/test.spy -m lexer 

# 进行语法分析输出语法树
python main.py -i test/test.spy -m parser 
```