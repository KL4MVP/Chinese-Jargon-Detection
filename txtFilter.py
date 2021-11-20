import pickle
words = [line.split() for line in open("./scores/dupin_scores.txt", 'r', encoding='utf-8').readlines()]
with open("./dubo_filter.txt","w") as f:

    for word in words:
        # print(float(word[1]))
        if float(word[1]) > 0:
            f.write(word[0]+" ")
            f.write(word[1]+" ")
            f.write(word[2])
            f.write(("\n"))
