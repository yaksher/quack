from collections import defaultdict
import numpy as np
import nltk
import os

CBOW_SIZE = 8 # Number of words to either side to look when training; doesn't affect the shape of the output.
DIMS = 10     # The number of dimensions the output vector for each word has.

def make_dict(dims):
    """Create a defaultdict object whose default value is a tuple
    of a random normal vector with dims dimensions and a 1 (the initial weight of the current value)
    """
    def random_hypersphere_point():
        v = np.random.normal(size=dims)
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm
    def default_func():
        return (random_hypersphere_point(), 1)
    return defaultdict(default_func)

word2vec = make_dict(DIMS)


# Convert training text to a list of words. Punctuation is ignored.
#training_file = open("SMBC_text_uncleaned.txt", "r")
#training_text = training_file.read()
#training_file.close()
#words = [word.lower() for word in words if word.lower() not in ["the","be","to","of","and","a","in","that","have","I","it","for","not","on","with","he","as","you","do","at","this","but","his","by","from","they","we","say","her","she"]]

print("getting training text")
training_text = "\n\n\n".join([open(txt_file, "r").read() for txt_file in os.listdir(".") if txt_file.endswith(".txt")])

print("converting to proper data")
data = [[word.lower() for word in nltk.word_tokenize(sent)] for sent in nltk.sent_tokenize(training_text)]

"""# Iterate over the list, ignoring the first and last CBOW to avoid dealing with it 
# because the length is expected to be many thousands (probably millions)
for i in range(CBOW_SIZE, len(words) - CBOW_SIZE):
    total = np.zeros((DIMS,)) # Create a zero vector.
    for j in range(i - CBOW_SIZE, i + CBOW_SIZE + 1):
        if j != i:
            total += word2vec[words[j]][0] # Add together the neighboring words
    total /= CBOW_SIZE * 2 # average them out.
    weight = word2vec[words[i]][1] # Get the weight of the word currently being modified
    total = total * 1 / (weight + 1) # Weight the total
    current = word2vec[words[i]][0] * weight / (weight + 1) # Weight the current.
    word2vec[words[i]] = (current + total, word2vec[words[i]][1] + 1) # Add current and total, increment the weight."""

from gensim.models import Word2Vec

print("training model")
model = Word2Vec(data, min_count = 1, size = 20, window = 9, sg = True)
model.save("word2vec.model")

#import pickle
#word2vec_no_def = {key: value for key, value in word2vec.items()}
#pickle.dump(word2vec_no_def, open("word2vec3.pickle", "wb"))