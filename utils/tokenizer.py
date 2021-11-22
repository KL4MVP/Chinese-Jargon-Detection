# encoding=utf-8
import re
import pandas as pd
import jieba
# add the result of new words discovery you need to this userdict.txt
jieba.load_userdict("./userdict.txt")

if __name__ == '__main__':

    corpus = [line.strip() for line in open("./processed.txt", 'r',
                                            encoding='utf-8').readlines()]  # read from clean data

    jieba_cut = []

    for line in corpus:
        seg_list = jieba.cut(str(line))
        jieba_cut.append(' '.join(list(seg_list)))  # segment with spaces

    new_df = pd.DataFrame()
    new_df["jieba_cut"] = jieba_cut
    # save segmentation result to cut.csv
    new_df.to_csv("./cut.csv", encoding="utf8")
