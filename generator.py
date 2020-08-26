import numpy as np
import tensorflow as tf
import re


class LyricsGenerator:
    """
    Generate lyrics using RNN
    """

    def __init__(self, lyrics):
        ly = ''.join(lyrics).lower()
        self.re_lyrics = re.sub(r'[^a-z0-9\'\!\?]', ' ', ly)
        self.vocab = sorted(set(self.re_lyrics))

        self.n_chars = len(self.re_lyrics)  # number of characters in lyrics
        self.n_vocab = len(self.vocab)  # number of vocabulary in lyrics

        self.vti = {v: i for i, v in enumerate(self.vocab)}  # vocab to index
        self.itv = np.array(self.vocab)  # index to vocab
        self.idx_lyrics = np.array([self.vti[ly] for ly in self.re_lyrics])  # indexed lyrics

    def model(self, embedding_dim, rnn_units, batch_size, dropout=0.2, activation='relu'):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Embedding(self.n_vocab, embedding_dim, batch_input_shape=[batch_size, None]))
        model.add(tf.keras.layers.LSTM(rnn_units, return_sequences=True, stateful=True,
                                       recurrent_initializer='he_uniform', ))
        model.add(tf.keras.layers.Dropout(dropout))
        model.add(tf.keras.layers.Dense(self.n_vocab, activation=activation))

        return model

    def generate_lyrics(self, model, input_string, num=1000, temp=0.5):
        new_lyrics = []

        vti_input = [self.vti[i] for i in input_string]
        vti_input = tf.expand_dims(vti_input, 0)

        model.reset_states()

        for i in range(num):
            pred = model(vti_input)
            pred = tf.squeeze(pred, 0)

            pred = pred / temp
            predicted_id = tf.random.categorical(pred, num_samples=1)[-1, 0].numpy()

            vti_input = tf.expand_dims([predicted_id], 0)

            new_lyrics.append(self.itv[predicted_id])

        return input_string + ''.join(new_lyrics)

    @staticmethod
    def xy_split(string):
        x = string[:-1]
        y = string[1:]
        return x, y

    @staticmethod
    def loss(labels, logits):
        return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)
