import re
import pickle
import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import to_array

import jieba
jieba.load_userdict("./userdict.txt")


def is_chinese(uchar):
    """
    判断一个unicode是否是汉字
    detect whether a unicode is Chinese
    """
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def format_str(content):
    """
    remain Chinese character in the dictionary examples
    remove other symbols
    """
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str + i
    return content_str


def coSim(vec1, vec2):
    """
    cosine similarity comparison
    """
    num = vec1.dot(vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = num / denom
    return sim


def framework(cat, tokenizer, model, filterWords, corpus, chineseDic):
    """
    Cross-corpus jargon detection framework
    INPUT: jargon candidates found by findCandidate.py
    OUTPUT: real jargons for each crime category
    """
    # read from jargon candidates found by findCandidate.py
    words = [line.split() for line in open(
        "./CANDIDATE/{}CANDIDATE.txt".format(cat), 'r', encoding='utf-8').readlines()]
    # sort them according to the similarity scores
    words.sort(key=lambda x: x[1], reverse=True)

    candidate = []
    # threshold for similarity between the word in darknet and the word in dictionary
    limit = 0.41
    # we use the top 400 candidate words for an example, you can also set the threshold for this
    for word in words[:400]:
        candidate.append(word[0])

    Jargon = []

    # traverse the candidates and cross-comparison between dictionary and seed criminal keywords
    for can in candidate:
        index = "【" + can + "】"
        flag = 0
        for line in chineseDic:
            # 词典中该词为单独条例，需要进行词向量对比
            # if the candidate is an entry in the dictionary, we find its example sentence
            if index in line:
                # find the original candidate embedding
                for filterword in filterWords:
                    if can in filterword:
                        sen = corpus[int(filterword[2])]
                        senten = emb[int(filterword[2])]
                        dark_emb = senten[sen.index(filterword[0]) + 1]
                print("IN THE TITLE")
                # preprocess the example sentence of the candidate
                line = line.replace(index, can + "是")
                line = line.replace("～", can).strip()
                line = re.sub(re.compile("〈.〉"), "", line)
                line = format_str(line)
                # make sure the candidate is clearly cut in the example sentence
                seg_list = list(jieba.cut(str(line)))
                new_list = []
                for seg in seg_list:
                    a = []
                    if can in seg:
                        seg = seg.replace(can, " " + can + " ")
                        a = seg.split(" ")
                    else:
                        a.append(seg)
                    new_list.extend(a)
                new_list = list(filter(None, new_list))
                new_list.insert(0, '[CLS]')
                new_list.insert(len(new_list), '[SEP]')
                pos = [i for i, x in enumerate(new_list) if x == can]
                token_ids, segment_ids = tokenizer.encode(new_list)
                if len(token_ids) > 512:
                    token_ids[511] = 102
                    token_ids = token_ids[:512]
                    segment_ids = segment_ids[:512]
                # generate the dictionary embedding
                bert_emb = model.predict(
                    [np.array([token_ids]), np.array([segment_ids])])
                dic_emb = bert_emb[0][pos[-1]]
                # compare the similarity of dark embedding and dictionary embedding
                th2 = coSim(dark_emb, dic_emb)
                # print("TH2:",th2)
                if th2 < limit:
                    Jargon.append(can)
                flag = 1
                break
            # 词典中该词在其他句子中出现，需要进行词向量对比
            # if the candidate is shown not in the entry but in the explanation of other entry
            elif can in line:
                try:
                  # find the original candidate embedding
                    for filterword in filterWords:
                        if can in filterword:
                            sen = corpus[int(filterword[2])]
                            senten = emb[int(filterword[2])]
                            dark_emb = senten[sen.index(filterword[0]) + 1]
                    print("IN THE LINE")
                    # preprocess the example sentence of the candidate
                    line = line.replace(index, can + "是")
                    line = line.replace("～", can).strip()
                    line = re.sub(re.compile("〈.〉"), "", line)
                    line = format_str(line)
                    # make sure the candidate is clearly cut in the example sentence
                    seg_list = list(jieba.cut(str(line)))
                    new_list = []
                    for seg in seg_list:
                        a = []
                        if can in seg:
                            seg = seg.replace(can, " " + can + " ")
                            a = seg.split(" ")
                        else:
                            a.append(seg)
                        new_list.extend(a)
                    new_list = list(filter(None, new_list))
                    new_list.insert(0, '[CLS]')
                    new_list.insert(len(new_list), '[SEP]')
                    pos = [i for i, x in enumerate(new_list) if x == can]
                    token_ids, segment_ids = tokenizer.encode(new_list)
                    if len(token_ids) > 512:
                        token_ids[511] = 102
                        token_ids = token_ids[:512]
                        segment_ids = segment_ids[:512]
                    # generate the dictionary embedding
                    bert_emb = model.predict(
                        [np.array([token_ids]), np.array([segment_ids])])
                    dic_emb = bert_emb[0][pos[-1]]
                    # compare the similarity of dark embedding and dictionary embedding
                    th2 = coSim(dark_emb, dic_emb)
                    # print("TH2:",th2)
                    if th2 < limit:
                        Jargon.append(can)
                    flag = 1
                    break
                except Exception as e:
                    continue
        # if the candidate jargon is not shown in the dictionary, we assume its a real jargon
        if flag == 0:
            print(can)
            print("It's Jargon")
            Jargon.append(can)
    return Jargon  # return final real jargon list


if __name__ == "__main__":
    # load your pretrained model
    config_path = './DC-BERT/bert_config.json'
    checkpoint_path = './DC-BERT/bert_model.ckpt'
    dict_path = './DC-BERT/vocab.txt'

    tokenizer = Tokenizer(
        dict_path, pre_tokenize=lambda s: jieba.cut(s))  # load tokenizer
    model = build_transformer_model(
        config_path, checkpoint_path)  # build DC-BERT model

    # load vocab
    filterWords = [line.split() for line in open(
        "./dupin_filter.txt", 'r', encoding='utf-8').readlines()]
    # load corpus
    corpus = [line.split() for line in open(
        "./seg.txt", 'r', encoding='utf-8').readlines()]
    # load embeddings
    with open("./bert_final_emb.pickle", "rb") as f:
        emb = pickle.load(f)

    chineseDic = []  # load Chinese dictionary
    with open('./XDHYCD7th.txt', 'r') as inF:
        for line in inF:
            chineseDic.append(line)

    # process all candidates of crimes
    cats = ["DUBO", "DUPIN", "GR", "HC", "HK",
            "LIAO", "QZ", "SQ", "XQ", "YM", "ZP"]
    for cat in cats:
        Jargons = framework(cat, tokenizer, model,
                            filterWords, corpus, chineseDic)
        print(Jargons)
        # save real jargons detected by our framework
        with open("./JARGON/{}.txt".format(cat), "w") as f:
            for jargon in Jargons:
                f.write(jargon + "\n")
