#!/usr/bin/env python3
import sys
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils


def extract_vocab(raw_text):
    chars = sorted(list(set(raw_text)))
    char_to_int = dict((c, i) for i, c in enumerate(chars))
    return char_to_int, len(chars)

def get_train_patterns(raw_text, vocab, vocabsize):
    seq_length = 100 #100 characters predict the next 1
    dataX = []
    dataY = []
    for i in range(0, len(raw_text) - seq_length, 1):
        seq_in = raw_text[i:i + seq_length]
        seq_out = raw_text[i + seq_length]
        dataX.append([vocab[char] for char in seq_in])
        dataY.append(vocab[seq_out])

    # reshape X to be [samples, time steps, features]
    X = numpy.reshape(dataX, (len(dataX), seq_length, 1))
    # normalize
    X = X / vocabsize
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)
    return X, y

def train_lstm(X,y, epochs=20, batch_size=128):
    model = Sequential()
    model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]))) #256 memory units
    model.add(Dropout(0.2)) #dropout probability
    model.add(Dense(y.shape[1], activation='softmax')) #The output layer is a Dense layer using the softmax activation function to output a probability prediction for each of the 47 characters between 0 and 1.
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callbacks_list = [checkpoint]

    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=callbacks_list)
    return model

if __name__ == '__main__':

    with open(sys.argv[1],'r',encoding='utf-8') as f:
        raw_text = f.read()

    vocab, vocabsize = extract_vocab(raw_text)
    X, y = get_train_patterns(raw_text, vocab, vocabsize)
    model = train_lstm(X,y)










