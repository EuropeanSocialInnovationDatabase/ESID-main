import pickle
from os import listdir
import os
from os.path import isfile, join

import numpy as np
import pandas as pd
import sklearn
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, Dropout, Conv1D, MaxPooling1D, Dense, Activation, Flatten, Bidirectional, LSTM
from keras.models import model_from_json, Sequential
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.cross_validation import cross_val_score, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline


class LSTMClassifier():
    def __init__(self):
        os.environ['PYTHONHASHSEED'] = '4'
        np.random.seed(523)
        self.max_words = 10000
        self.batch_size = 16
        self.epochs = 100
        self.GLOVE_DIR = "../../../Helpers/BratDataProcessing/Glove_dir"
        self.MAX_SEQUENCE_LENGTH = 1100
        self.EMBEDDING_DIM = 200
        pass

    def train_LSTM_words_only(self,X_train,y_train):
        embeddings_index = {}
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.tokenizer.fit_on_texts(X_train)
        sequences = self.tokenizer.texts_to_sequences(X_train)

        word_index = self.tokenizer.word_index
        f = open(os.path.join(self.GLOVE_DIR, 'glove.6B.200d.txt'))
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        print('Found %s word vectors.' % len(embeddings_index))
        embedding_matrix = np.zeros((len(word_index) + 1, self.EMBEDDING_DIM))
        for word, i in word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
        embedding_layer = Embedding(len(word_index) + 1,
                                    self.EMBEDDING_DIM,
                                    weights=[embedding_matrix],
                                    input_length=self.MAX_SEQUENCE_LENGTH,
                                    trainable=False)

        early_stopping = EarlyStopping(monitor='val_loss', patience=5)
        y_train = to_categorical(y_train)
        model = None
        model = Sequential()
        model.add(embedding_layer)
        # model.add(Dropout(0.2))
        # model.add(Conv1D(filters=512, kernel_size=2, padding='same', activation='relu'))
        # model.add(MaxPooling1D(pool_size=2))
        # model.add(Dropout(0.2))
        # model.add(Conv1D(filters=256, kernel_size=2, padding='same', activation='relu'))
        # model.add(MaxPooling1D(pool_size=2))
        # model.add(Dropout(0.2))
        # model.add(Conv1D(filters=128, kernel_size=2, padding='same', activation='relu'))
        # model.add(MaxPooling1D(pool_size=2))
        # model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(500,recurrent_dropout=0.4,dropout=0.2)))
        #model.add(Flatten())
        model.add(Dense(2))
        model.add(Dropout(0.2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit(data, y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=1,
                                validation_split=0.1,
                                callbacks=[early_stopping]
                                )
        self.clf = model

    def save_LSTM_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.tokenizer, open(path + "/tokenizer.pck", 'wb'))
        model_json = self.clf.to_json()
        with open(path+"/model_actors.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.clf.save_weights(path+"/model_actors.h5")

    def load_LSTM_model(self,path):
        json_file = open(path+"/model_actors.json", 'r')
        loaded_model_json = json_file.read()
        self.tokenizer = pickle.load(open(path + "/tokenizer.pck", 'rb'))
        json_file.close()
        self.clf = model_from_json(loaded_model_json)
        # load weights into new model
        self.clf.load_weights(path+"/model_actors.h5")
        return self


    def predict_LSTM(self,X_test):
        sequences = self.tokenizer.texts_to_sequences(X_test)
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        y_pred = self.clf.predict(data)
        y_binary = []
        for y in y_pred:
            if y[0] < 0.5:
                y_binary.append(1)
            else:
                y_binary.append(0)
        return y_binary

    def print_reports(self,y_pred,y_test):
        print(sklearn.metrics.classification_report(y_pred, y_test))
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test)
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        print(new_confusion_matrix)




directory = "../../Dataset_SI_DB_Classification/"
onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
texts = []
objectives =[]
actors = []
outputs = []
innovativeness = []
si = []
for file in onlyfiles:
    f = open(directory + "/"+file, "r")
    text =  f.read()
    parts = file.split("_")
    ob = int(parts[2])
    ac = int(parts[3])
    ou = int(parts[4])
    ino = int(parts[5])
    sis = parts[6]
    text = str(text)
    if len(text)<300:
        continue
    texts.append(text)
    if ob>1:
        objectives.append(1)
    else:
        objectives.append(0)
    actors.append(ac)
    outputs.append(ou)
    innovativeness.append(ino)


text_clf = Pipeline([('vect', CountVectorizer()),
                      ('tfidf', TfidfTransformer()),
                      ('clf', RandomForestClassifier(n_estimators=200, max_depth=None, random_state=0)),
 ])
df = pd.DataFrame({'text': texts, 'classa': objectives})
train_df, test_df = train_test_split(df, test_size=0.1)
folder = sklearn.model_selection.KFold(5)
i = 0
# for train_index,test_index in folder.split(train_df):
#     i = i +1
#     print("FOLD:"+str(i))
#     cls = LSTMClassifier()
#     X_train = train_df['text'][train_index]
#     y_train = train_df['classa'][train_index]
#     cls.train_LSTM_words_only(X_train,y_train)
#     X_test= train_df['text'][test_index]
#     y_test = train_df['classa'][test_index]
#     y_pred = cls.predict_LSTM(X_test)
#     cls.print_reports(y_pred, y_test)
cls = LSTMClassifier()
X_train = train_df['text']
y_train = train_df['classa']
cls.train_LSTM_words_only(X_train, y_train)
cls.save_LSTM_model("Objectives_LSTM")
y_pred = cls.predict_LSTM(test_df['text'])
cls.print_reports(y_pred, test_df['classa'])
print("End of Objectives")


# scores = cross_val_score(text_clf, texts, objectives, cv=10,scoring='f1')
# final = 0
# for score in scores:
#     final = final + score
# print scores
# print "Final:" + str(final/10)