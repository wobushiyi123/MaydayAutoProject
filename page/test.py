import logging
import os
import re
# 第一个字符串反转，去除大写字母
# def reverse_str(str):
#     reverse_string=str[::-1]
#     cleaned_str=re.sub("[A-Z]","",reverse_string)
#     return cleaned_str
#
# input_str='Hello Word'
# output_str=reverse_str(input_str)
# print('原始字符串',input_str)
# print('变更后字符串',output_str)
# 去除相同字符串
# def cleanArray(array):
#     # new_list = set(array)
#     # print(new_list)
#     list_b=[]
#     for i in array:
#         if i not in list_b:
#             list_b.append(i)
#     print(list_b)
# arry=['1',"2","1","3","1"]
# cleanArray(arry)

# 找寻出一个目录下所有的文件名
files=os.listdir("D:\面试\面试题合集")
for i in files:
    print(i)