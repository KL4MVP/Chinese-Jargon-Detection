import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allocator_type = 'BFC' #A "Best-fit with coalescing" algorithm, simplified from a version of dlmalloc.
set_session(tf.Session(config=config))
import os
import numpy as np
import pyprind
import pickle
from tokenPos import search
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import to_array
import jieba
import time
jieba.load_userdict("./userdict.txt")
# import os
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def coSim(vec1,vec2):
    num = vec1.dot(vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = num / denom
    return sim

# def ED(vec1,vec2):
#     return np.linalg.norm(vec1-vec2)

def getRow(pos):
    return pos[0]

def getColumn(pos):
    return pos[1]




corpus = [line.split() for line in open("./seg.txt", 'r', encoding='utf-8').readlines()]

# print(corpus)
'''
with open("./corpus.pickle","rb") as f:
    corpus = pickle.load(f)
'''

with open("./bert_final_emb.pickle","rb") as f:
    emb = pickle.load(f)

# 根据实际情况进行修改
config_path = './fine-tune5/bert_config.json'
checkpoint_path = './fine-tune5/bert_model.ckpt'
dict_path = './fine-tune5/vocab.txt'

tokenizer = Tokenizer(dict_path, do_lower_case=True, pre_tokenize=lambda s: jieba.cut(s))  # 建立分词器
model = build_transformer_model(config_path, checkpoint_path)  # 建立

print(len(corpus))
print(len(emb))


# print(corpus[31097])


vocab = [line.strip() for line in open("./remain.txt", 'r', encoding='utf-8').readlines()]

KeyW = "毒品"
print(tokenizer.tokenize(KeyW))
#print(len(tokenizer.tokenize(KeyW)))
token_ids, segment_ids = tokenizer.encode(KeyW)
KeyV = model.predict([np.array([token_ids]), np.array([segment_ids])])

pbar = pyprind.ProgBar(len(vocab[3:]),title='进度展示',monitor=True)

t1 = time.time()

with open("./dp_scores.txt","w",encoding='utf-8') as f:
    for word in vocab[3:]:
    # word = "自动"
        #print(word)
        positions = search(corpus,word)
        # print(positions)

        sen_vec = []
        word_vec = []
        scores = []

        for i in range(len(positions)):
            # print(corpus[getRow(positions[i])])
            # print(i)
            #print(positions[i])
            senten = emb[getRow(positions[i])]
            col = getColumn(positions[i])
            #if col > 510:
            if col+1>=511:
                scores.append(0)
                #print(positions[i])
                continue
            else:
                word_v = senten[col+1]
                sim = torch.cosine_similarity(torch.tensor(word_v),torch.tensor(KeyV[0,0,:]),dim=0).to(device).item()
                sim = coSim(word_v,KeyV[0][1])
                # sim = ED(word_v,KeyV[0][1])
                print(word_v.shape)
                print(KeyV[0,0,:].shape)
                print(sim)
                scores.append(sim)
        #print(max(scores))
        f.write(word+" ")
        f.write(str(max(scores))+" ")
        f.write(str(getRow(positions[scores.index(max(scores))]))+"\n")
        pbar.update()
print(pbar)
t2=time.time()
print(t2-t1)
