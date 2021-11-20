# encoding=utf-8
import jieba
jieba.load_userdict("./userdict.txt")
import pandas as pd
import re

corpus = [line.strip() for line in open("./processed_3.txt", 'r', encoding='utf-8').readlines()]

paddle_cut = []
jieba_cut = []
for text in corpus:

    seg_list1 = jieba.cut(str(text))
    jieba_cut.append(' '.join(list(seg_list1)))

with open("seg.txt","w") as f:
    for j in jieba_cut:
        f.write(j)
        f.write("\n")
