import sys
from matplotlib import pyplot
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, GRU
from keras.layers.embeddings import Embedding
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from random import shuffle

EMBEDDING_DIM = 20

file = open("rp-ooc-rip.txt", "r")
ooc_text = ''.join([chunk for chunk in file])
file.close()
file = open("rp-rwby-ooc-rip.txt", "r")
ooc_text += ''.join([chunk for chunk in file])
file.close()
file = open("rp-sao-rip.txt", "r")
inc_text = ''.join([chunk for chunk in file])
file.close()
file = open("rp-rwby-rip.txt", "r")
inc_text += ''.join([chunk for chunk in file])
file.close()
ooc_text, inc_text = ooc_text.split("{r}"), inc_text.split("{r}")

total_data = ooc_text + inc_text
tokenizer_obj = Tokenizer()#(char_level=True, filters='\n')
tokenizer_obj.fit_on_texts(total_data)

max_length = max([len(s.split()) for s in total_data])

vocab_size = len(tokenizer_obj.word_index) + 1
data = [(s,0) for s in inc_text] + [(s,1) for s in ooc_text]
shuffle(data)
data_len = len(data)
print(data_len)
t_frac = (2 * data_len) // 3
x_data, y_data = [e[0] for e in data], [e[1] for e in data]
x_train, x_test, y_train, y_test = x_data[:t_frac], x_data[t_frac:], y_data[:t_frac], y_data[t_frac:]

x_train_tokens =  tokenizer_obj.texts_to_sequences(x_train)
x_test_tokens =  tokenizer_obj.texts_to_sequences(x_test)
x_train_pad = pad_sequences(x_train_tokens, maxlen=max_length, padding='post')
x_test_pad = pad_sequences(x_test_tokens, maxlen=max_length, padding='post')


model = Sequential([
Embedding(vocab_size, EMBEDDING_DIM, input_length=max_length),
LSTM(32, dropout = .5, recurrent_dropout = .5, return_sequences = True),
LSTM(32, dropout = .5, recurrent_dropout = .5),
Dense(1, activation='softmax')
])
model.compile(loss='binary_crossentropy', optimizer='adam')

history = model.fit(x_train_pad, y_train, epochs=100, batch_size=32,
                    validation_data=(x_test_pad, y_test), verbose=1, shuffle=False,
                    callbacks=[
                    EarlyStopping(monitor='loss', patience=8, min_delta = .00001),
                    ReduceLROnPlateau(monitor='loss', factor=0.3, patience=4)#,
                    #keras.callbacks.TensorBoard(log_dir="/srv/log/", histogram_freq=0, write_grads=False, write_graph=False, write_images=False)
                    ])

if len(sys.argv) >= 2:
    model.save(sys.argv[1])

predictions = model.predict(x_test_pad, verbose=1)
count = 0
for i in range(len(y_test)):
    if round(predictions[i][0]) == y_test[i]:
        count += 1
print("Accuracy:", round(count/len(y_test),4))
print("Correct: " + str(count) + "/" + str(len(y_test)))

pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()
