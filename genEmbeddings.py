import os
import numpy as np
import pyprind
import pickle
import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import to_array
import jieba
# add the result of new words discovery you need to this userdict.txt
jieba.load_userdict("./userdict.txt")

if __name__ == '__main__':
    """
    Generate darknet WORD embeddings from DC-BERT
    """

    corpus = [line.strip() for line in open("./processed.txt", 'r',
                                            encoding='utf-8').readlines()]  # read from clean data

    # load your pretrained model
    config_path = './DC-BERT/bert_config.json'
    checkpoint_path = './DC-BERT/bert_model.ckpt'
    dict_path = './DC-BERT/vocab.txt'

    tokenizer = Tokenizer(
        dict_path, pre_tokenize=lambda s: jieba.cut(s))  # load tokenizer
    model = build_transformer_model(
        config_path, checkpoint_path)  # build DC-BERT model

    emb = []

    pbar = pyprind.ProgBar(len(corpus), title='进度展示', monitor=True)
    for corpu in corpus:
        tokenizer.tokenize(corpu)
        token_ids, segment_ids = tokenizer.encode(corpu)
        # the DC-BERT is trained with max_seq_len of 512, so cannot deal with sentence longer than 512 characters
        if len(token_ids) > 512:
            token_ids[511] = 102
            token_ids = token_ids[:512]
            segment_ids = segment_ids[:512]

        bert_emb = model.predict(
            [np.array([token_ids]), np.array([segment_ids])])
        # print(bert_emb.shape)
        emb.extend(bert_emb)
        pbar.update()
    print(pbar)
    print("Starting to Save Embeddings.")
    print("Length:", len(emb))
    with open("bert_final_emb.pickle", "wb") as f:
        pickle.dump(emb, f, protocol=4)
    print("Saving Successfully.")
