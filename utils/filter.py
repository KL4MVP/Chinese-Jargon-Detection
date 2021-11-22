# 创建停用词list
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords

def filter(filepath,stopwords):
    vocab = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    with open("./remain.txt","w") as outputs:
        for word in vocab:
            if word not in stopwords:
                outputs.write(word+"\n")
    outputs.close()

if __name__ == "__main__":
    """
    INPUT: vocab.txt: all unique words from the corpus
    OUTPUT: remain.txt
    remove stop words from vocab.txt
    """

    baidu = stopwordslist("./stopwords/baidu_stopwords.txt")
    cn = stopwordslist("./stopwords/cn_stopwords.txt")
    hit = stopwordslist("./stopwords/hit_stopwords.txt")
    scu = stopwordslist("./stopwords/scu_stopwords.txt")
    stopwords = baidu + cn + hit + scu
    filter("./vocab.txt",stopwords)
