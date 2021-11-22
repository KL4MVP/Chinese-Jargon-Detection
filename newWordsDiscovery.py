import extract_phrase
import pandas as pd
import re
import time
import pandas as pd
import numpy as np

if __name__ == '__main__':

    # read from clean data
    df = pd.read_csv("./processed.csv", encoding="utf8")
    # print(df["processed"].head())
    corpus = df["processed"].to_list()

    t1 = time.time()
    # extract new words using entropy and mutual-information
    result = extract_phrase(corpus, top_k=1, min_freq=1, max_n=4, min_n=1)
    t2 = time.time()
    print(result[:400])

    # save new words to new_words.txt and sorted with T-score
    with open("./new_words.txt", "w") as f:
        for line in result:
            f.write(line[0] + " ")
            f.write(str(line[1]) + "\n")

    print("time:", t2 - t1)
