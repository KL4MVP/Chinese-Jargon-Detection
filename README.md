# An Unsupervised Detection Framework for Chinese Jargons in the Darknet

This repo is the Python 3 implementation of 《An Unsupervised Detection Framework for Chinese Jargons in the Darknet》 (Proceedings of the Fifteenth ACM International Conference on Web Search and Data Mining (WSDM ’22).

## Introduction

This project proposes Chinese jargon detection framework based on unsupervised learning.

## Requirements

```bash
pip install -r requirements.txt
```

## Data

- Due to the sensitivity of the darknet information, we will not distribute the dataset directly, we show some samples of dataset in /dataset/sample.csv and we will leave the contact information for readers to request for Raw Corpus.

  Please contact Liang Ke (keliang001@stu.scu.edu.cn) for the Darknet corpus dataset.

- The Modern Chinese Dictionary (the 7th edition) that we used for cross-corpus comparison is from [here](https://github.com/CNMan/XDHYCD7th).

## Code

1. Preprocess the raw corpus using `preprocess.py` and get the clean corpus.
2. Find out-of-vocabulary words using `newWordsDiscovey.py`, and add them to tokenizer dictionary.
3. Pretrain word-based DC-BERT model with clean corpus using `pretrain.py`.
4. Generate word embeddings with pretrained DC-BERT using `genEmbedding.py`.
5. Consruct seed criminal keywords with `findSeedKeywords.py`, we show an example of a list of seed criminal keywords for readers to reference, you can either delete or add words related to your task.
6. Find jargon candidates (words related to relevant cybercrimes and are very likely to be jargons) with `findCandidate.py`.
7. Finally, you can obtain real darknet Chinese jargons detected by our framework using `findJargon.py`.

## Citation
