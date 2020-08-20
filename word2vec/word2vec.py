import numpy as np
import nltk
import os

DIMS = 20     # The number of dimensions the output vector for each word has.

print("getting training text")
training_text = "\n\n\n".join([open(txt_file, "r").read() for txt_file in os.listdir(".") if txt_file.endswith(".txt")])

print("converting to proper data")
data = [[word.lower() for word in nltk.word_tokenize(sent)] for sent in nltk.sent_tokenize(training_text)]

from gensim.models import Word2Vec

print("training model")
model = Word2Vec(data, min_count = 1, size = DIMS, window = 9, sg = True)
model.save("word2vec.model")