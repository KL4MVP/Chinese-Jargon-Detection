#! -*- coding: utf-8 -*-
# Word-based DC-BERT pretraining on Chinese darknet corpus with MLM task


import os
import json
import numpy as np
from bert4keras.backend import keras, K
from bert4keras.layers import Loss
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer, load_vocab, save_vocab
from bert4keras.optimizers import Adam
from bert4keras.optimizers import extend_with_weight_decay
from bert4keras.optimizers import extend_with_gradient_accumulation
from bert4keras.snippets import sequence_padding, open
from bert4keras.snippets import DataGenerator
from bert4keras.snippets import text_segmentate
import jieba
jieba.initialize()
# add the result of new words discovery you need to this userdict.txt
jieba.load_userdict("./userdict.txt")


# 基本参数
# basic params
maxlen = 256
batch_size = 32
epochs = 500
num_words = 61711


# read from RoBERTa-wwm-ext model
config_path = '/home/kl/darknet/RoBERTa-wwm-ext/bert_config.json'
checkpoint_path = '/home/kl/darknet/RoBERTa-wwm-ext2/bert_model.ckpt'
dict_path = '/home/kl/darknet/RoBERTa-wwm-ext/vocab.txt'


def corpus():
    """
    corpus generator
    read from clean data
    """
    while True:
        files = './processed.txt'
        with open(files, "r") as f:
            for l in f:
                for text in text_process(l):
                    yield text


def text_process(text):
    """
    text segmentation
    """
    texts = text_segmentate(text, 32, u'\n。')
    result, length = '', 0
    for text in texts:
        if result and len(result) + len(text) > maxlen * 1.3:
            yield result
            result, length = '', 0
        result += text
    if result:
        yield result


if os.path.exists('tokenizer_config.json'):
    token_dict,  compound_tokens = json.load(
        open('tokenizer_config.json')
    )
else:
    # 加载并精简词表
    # load and simplify vocab
    token_dict = load_vocab(
        dict_path=dict_path,
        simplified=False,
        startswith=['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'],
    )
    pure_tokenizer = Tokenizer(token_dict.copy(), do_lower_case=True)
    # add all unique words from corpus to ./v2/vocab.txt
    words = [line.strip() for line in open(
        "./v2/vocab.txt", 'r', encoding='utf-8').readlines()]
    # print(words)
    user_dict = []
    for w in words[3:]:
        if w not in token_dict:
            token_dict[w] = len(token_dict)
            user_dict.append(w)
        if len(user_dict) == num_words:
            break
    compound_tokens = [pure_tokenizer.encode(w)[0][1:-1] for w in user_dict]
    json.dump([token_dict,  compound_tokens],
              open('tokenizer_config.json', 'w'))

tokenizer = Tokenizer(
    token_dict,
    do_lower_case=True,
    pre_tokenize=lambda s: jieba.cut(s) # add a pre-tokenize here
)

# save_vocab("./wovocab.txt",token_dict)


def random_masking(token_ids):
    """
    对输入进行随机mask
    random mask the input
    """
    rands = np.random.random(len(token_ids))
    source, target = [], []
    for r, t in zip(rands, token_ids):
        if r < 0.15 * 0.8:
            source.append(tokenizer._token_mask_id)
            target.append(t)
        elif r < 0.15 * 0.9:
            source.append(t)
            target.append(t)
        elif r < 0.15:
            source.append(np.random.choice(tokenizer._vocab_size - 1) + 1)
            target.append(t)
        else:
            source.append(t)
            target.append(0)
    return source, target


class data_generator(DataGenerator):
    """数据生成器
    """

    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids, batch_output_ids = [], [], []
        for is_end, text in self.sample(random):
            token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
            source, target = random_masking(token_ids)
            batch_token_ids.append(source)
            batch_segment_ids.append(segment_ids)
            batch_output_ids.append(target)
            if len(batch_token_ids) == self.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_output_ids = sequence_padding(batch_output_ids)
                yield [
                    batch_token_ids, batch_segment_ids, batch_output_ids
                ], None
                batch_token_ids, batch_segment_ids, batch_output_ids = [], [], []


class CrossEntropy(Loss):
    """交叉熵作为loss，并mask掉输入部分
    """

    def compute_loss(self, inputs, mask=None):
        y_true, y_pred = inputs
        y_mask = K.cast(K.not_equal(y_true, 0), K.floatx())
        accuracy = keras.metrics.sparse_categorical_accuracy(y_true, y_pred)
        accuracy = K.sum(accuracy * y_mask) / K.sum(y_mask)
        self.add_metric(accuracy, name='accuracy')
        loss = K.sparse_categorical_crossentropy(
            y_true, y_pred, from_logits=True
        )
        loss = K.sum(loss * y_mask) / K.sum(y_mask)
        return loss


bert = build_transformer_model(
    config_path,
    checkpoint_path,
    with_mlm='linear',
    #    keep_tokens=keep_tokens,  # only keep characters from kee_tokens
    # add words and initialize with average character embeddings
    compound_tokens=compound_tokens,
    return_keras_model=False
)


y_in = keras.layers.Input(shape=(None,))
outputs = CrossEntropy(1)([y_in, model.output])

train_model = keras.models.Model(model.inputs + [y_in], outputs)

AdamW = extend_with_weight_decay(Adam, name='AdamW')
AdamWG = extend_with_gradient_accumulation(AdamW, name='AdamWG')
optimizer = AdamWG(
    learning_rate=5e-6,
    weight_decay_rate=0.01,
    exclude_from_weight_decay=['Norm', 'bias'],
    grad_accum_steps=16,
)
train_model.compile(optimizer=optimizer)
train_model.summary()


class Evaluator(keras.callbacks.Callback):
    """训练回调
    """

    def on_epoch_end(self, epoch, logs=None):
        model.save_weights('bert_model.weights')  # 保存模型


if __name__ == '__main__':

    # 启动训练
    evaluator = Evaluator()
    train_generator = data_generator(corpus(), batch_size, 10**5)

    train_model.fit_generator(
        train_generator.forfit(),
        steps_per_epoch=1048,
        epochs=epochs,
        callbacks=[evaluator]
    )

    # train_model.load_weights("bert_model.weights")
    # train_model.save_weights_as_checkpoint("bert_model.ckpt")

else:

    model.load_weights('bert_model.weights')
