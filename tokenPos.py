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
