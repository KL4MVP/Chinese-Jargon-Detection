import pandas as pd
import pickle





def search(corpus,pattern):
    positions = []
    col = 0
    for sentence in corpus:
        if pattern in sentence:
            row = sentence.index(pattern)
            pos = (col,row)
            # print(pos)
            positions.append(pos)
        col += 1
    return positions





# with open("./corpus.pickle","rb") as f:
#     corpus = pickle.load(f)
# positions = search(corpus,"草榴")
# print(positions)
# for pos in positions:
#     print(corpus[pos[0]])
