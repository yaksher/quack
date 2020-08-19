from gensim.models import KeyedVectors
from nltk import word_tokenize
import numpy as np
import pickle

wv = KeyedVectors.load("word2vec.kv", mmap="r")
shape = wv["and"].shape

count = 0
common_words = ["the","be","to","of","and","a","in","that","have","I","it","for","not","on","with","he","as","you","do","at","this","but","his","by","from","they","we","say","her","she"]

def vec(word):
    global count
    if word in common_words:
        return np.zeros(shape)
    try:
        return wv[word.lower()]
    except KeyError:
        count += 1
        return np.zeros(shape)

def norm(vec):
    n = np.linalg.norm(vec)
    if n == 0:
        return vec
    return vec / n

import csv
smbc_file = open("SMBC_Full_Text.csv", newline="")
smbc_reader = csv.reader(smbc_file)
link_prefix = "https://www.smbc-comics.com/comic/"
next(smbc_reader)
next(smbc_reader)
comics = {row[0][len(link_prefix):]: word_tokenize(" ".join(row[1:])) for row in smbc_reader}
comic_vecs = {comic: norm(sum([vec(word) for word in text])) for comic, text in comics.items()}
print(count)
pickle.dump(comic_vecs, open("comic_vecs.pickle", "wb"))