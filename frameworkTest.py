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
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

def format_str(content):
    # content = unicode(content,'utf-8')
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str+i
    return content_str

def coSim(vec1,vec2):
    num = vec1.dot(vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = num / denom
    return sim

def framework(cat,tokenizer,model,filterWords,corpus,chineseDic):
    words = [line.split() for line in open("./CANDIDATE/{}CANDIDATE.txt".format(cat), 'r', encoding='utf-8').readlines()]
    words.sort(key=lambda x:x[1],reverse=True)
    # print(words[:100])

    candidate = []
    limit = 0.41
    
    for word in words[:400]:
        # print(word)
        candidate.append(word[0])

    print(len(candidate))
    Jargon = []

    for can in candidate:
        index = "【"+can+"】"
        flag = 0
        for line in chineseDic:
            # 词典中该词为单独条例，需要进行词向量对比
            if index in line:
                # 找出原词向量
                for filterword in filterWords:
                    if can in filterword:
                        sen = corpus[int(filterword[2])]
                        # print(sen)
                        senten = emb[int(filterword[2])]
                        dark_emb = senten[sen.index(filterword[0])+1]
                print(index)
                print(sen)
                print("IN THE TITLE")
                line = line.replace(index,can+"是")
                line = line.replace("～",can).strip()
                line = re.sub(re.compile("〈.〉"),"",line)
                line = format_str(line)

                # jieba.add_word(can,"10000000")
                seg_list = list(jieba.cut(str(line)))
                new_list = []
                for seg in seg_list:
                    a = []
                    if can in seg:
                        seg = seg.replace(can," "+can+" ")
                        a = seg.split(" ")
                    else:
                        a.append(seg)
                    new_list.extend(a)
                new_list = list(filter(None,new_list))
                new_list.insert(0,'[CLS]')
                new_list.insert(len(new_list),'[SEP]')
                # print(new_list)
                pos = [i for i,x in enumerate(new_list) if x==can]
                # print(pos[-1])
                # jieba.del_word(can)
                token_ids, segment_ids = tokenizer.encode(new_list)
                # KeyV = model.predict([np.array([token_ids]), np.array([segment_ids])])
                if len(token_ids) > 512:
                    token_ids[511] = 102
                    token_ids = token_ids[:512]
                    segment_ids = segment_ids[:512]
                # print(token_ids, segment_ids)
                # print(len(token_ids))
                # print(len(segment_ids))
                bert_emb = model.predict([np.array([token_ids]), np.array([segment_ids])])
                # print(bert_emb.shape)
                dic_emb = bert_emb[0][pos[-1]]
                # print(bert_emb[0][pos[-1]])

                th2 = coSim(dark_emb,dic_emb)
                print("TH2:",th2)
                if th2 < limit:
                    Jargon.append(can)

                flag = 1
                break
            # 词典中该词在其他句子中出现，需要进行词向量对比
            elif can in line:
                try:
                  # 找出原词向量
                    for filterword in filterWords:
                        if can in filterword:
                            sen = corpus[int(filterword[2])]
                            # print(sen)
                            senten = emb[int(filterword[2])]
                            dark_emb = senten[sen.index(filterword[0])+1]

                    print(can)
                    print(sen)
                    print("IN THE LINE")
                    # 格式化并分词，找到词语位置
                    line = line.replace(index,can+"是")
                    line = line.replace("～",can).strip()
                    line = re.sub(re.compile("〈.〉"),"",line)
                    line = format_str(line)

                    # jieba.add_word(can,"10000000")
                    seg_list = list(jieba.cut(str(line)))
                    new_list = []
                    for seg in seg_list:
                        a = []
                        if can in seg:
                            seg = seg.replace(can," "+can+" ")
                            a = seg.split(" ")
                        else:
                            a.append(seg)
                        new_list.extend(a)
                    new_list = list(filter(None,new_list))
                    new_list.insert(0,'[CLS]')
                    new_list.insert(len(new_list),'[SEP]')
                    # print(new_list)
                    pos = [i for i,x in enumerate(new_list) if x==can]
                    # print(pos[-1])
                    # jieba.del_word(can)
                    # 生成词典中词向量
                    token_ids, segment_ids = tokenizer.encode(new_list)
                    # KeyV = model.predict([np.array([token_ids]), np.array([segment_ids])])
                    if len(token_ids) > 512:
                        token_ids[511] = 102
                        token_ids = token_ids[:512]
                        segment_ids = segment_ids[:512]
                    # print(token_ids, segment_ids)
                    # print(len(token_ids))
                    # print(len(segment_ids))
                    bert_emb = model.predict([np.array([token_ids]), np.array([segment_ids])])
                    # print(bert_emb.shape)
                    dic_emb = bert_emb[0][pos[-1]]
                    # print(bert_emb[0][pos[-1]])

                    # 计算相似度
                    th2 = coSim(dark_emb,dic_emb)
                    print("TH2:",th2)
                    if th2 < limit:
                        Jargon.append(can)

                    flag = 1
                    break
                except Exception as e:
                    continue
        # 未在词典中出现
        if flag == 0:
            print(can)
            print("It's Jargon")
            Jargon.append(can)

    return Jargon



if __name__ == "__main__":
    # 模型加载地址
    config_path = './WOBERT/bert_config.json'
    checkpoint_path = './WOBERT/bert_model.ckpt'
    dict_path = './WOBERT/vocab.txt'

    tokenizer = Tokenizer(dict_path, do_lower_case=True, pre_tokenize=lambda s: jieba.cut(s, HMM=False))
    model = build_transformer_model(config_path, checkpoint_path)  # 建立

    filterWords = [line.split() for line in open("./dupin_filter.txt", 'r', encoding='utf-8').readlines()]
    corpus = [line.split() for line in open("./seg.txt", 'r', encoding='utf-8').readlines()]
    with open("./bert_final_emb.pickle","rb") as f:
        emb = pickle.load(f)

    chineseDic = []
    with open('./XDHYCD7th.txt', 'r') as inF:
        for line in inF:
            chineseDic.append(line)


    # cats = ["DUBO"]
    cats = ["DUBO","DUPIN","GR","HC","HK","LIAO","QZ","SQ","XQ","YM","ZP"]
    for cat in cats:
        Jargons = framework(cat,tokenizer,model,filterWords,corpus,chineseDic)
        print(Jargons)

        with open("./JARGON/{}.txt".format(cat),"w") as f:
            for jargon in Jargons:
                f.write(jargon+"\n")
