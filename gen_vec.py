import os
import numpy as np
import pyprind
import pickle
# from tokenPos import search
# import os
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import to_array
import jieba
jieba.load_userdict("./userdict.txt")

def coSim(vec1,vec2):
    num = vec1.dot(vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = num / denom
    return sim

def getRow(pos):
    return pos[0]

def getColumn(pos):
    return pos[1]


corpus = [line.strip() for line in open("./processed_3.txt", 'r', encoding='utf-8').readlines()]

# with open("./corpus.pickle","rb") as f:
#     corpus = pickle.load(f)

# 根据实际情况进行修改
config_path = './fine-tune5/bert_config.json'
checkpoint_path = './fine-tune5/bert_model.ckpt'
dict_path = './fine-tune5/vocab.txt'

tokenizer = Tokenizer(dict_path, pre_tokenize=lambda s: jieba.cut(s))  # 建立分词器
model = build_transformer_model(config_path, checkpoint_path)  # 建立


seg_corpus = []
emb = []

# pbar = pyprind.ProgBar(len(corpus[:10]),title='进度展示',monitor=True)
i = 0
for corpu in corpus:
    # print(corpu)
    # elmo_context_output_ = trainVec([corpu], model, output, batcher, context_token_ids)
    #tok = tokenizer.tokenize(corpu)
    #seg_corpus.append(tok)
    #i+=1
    #print(i)

#with open("corpus.pickle","wb") as f:
    #pickle.dump(seg_corpus,f)

    tokenizer.tokenize(corpu) 
    token_ids, segment_ids = tokenizer.encode(corpu)
    if len(token_ids) > 512:
        token_ids[511] = 102
        token_ids = token_ids[:512]
        segment_ids = segment_ids[:512]
    bert_emb = model.predict([np.array([token_ids]), np.array([segment_ids])])
    # print(bert_emb.shape)
    # print(bert_emb)
    emb.extend(bert_emb)
    i+=1
    print(i)
    
    '''
    if i%10000 ==0:
        with open("bert_{}.pickle".format(i),"wb") as f:
            pickle.dump(emb,f,protocol=4)
    '''
#     pbar.update()
# print(pbar)
print("starting save")
print("length:",len(emb))
with open("bert_final_emb.pickle","wb") as f:
    pickle.dump(emb,f,protocol=4)
print("save success")

