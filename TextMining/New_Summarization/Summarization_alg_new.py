import os
import pickle

import pandas as pd
import sklearn
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dropout, Flatten, Dense, Activation, LSTM, Bidirectional
from keras.models import model_from_json, Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import numpy as np
from sklearn.utils import resample

f = open("sentences_dataset_summaries_new_datasets.txt",'r')
lines = f.readlines()
data = []
for l in lines:
    dp = l.split('\t')
    tx = ""
    for d in range(0,len(dp)-1):
        tx = tx+" "+dp[d]
    data.append((dp[0],int(dp[-1].replace('\n',''))))
texts = []
labels = []
for d in data:
    texts.append(d[0])
    labels.append(d[1])
d = {'texts':texts,'labels':labels}
df = pd.DataFrame(data=d)
print(df.columns)

f_majority = df[df['labels']==0]
df_minority = df[df['labels']==1]
# f_majority_upsampled = resample(f_majority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=59850,    # to match majority class
#                                  random_state=83293) # reproducible results
df_upsampled = pd.concat([df_minority, f_majority])
df = df_upsampled.sample(frac=1).reset_index(drop=True)
print(df.groupby('labels').count())
texts2 = df['texts'].values
labels2 = df['labels'].values
train = texts2[0:int(0.8*len(texts2))]
trainY = labels2[0:int(0.8*len(labels2))]
test = texts2[int(0.8*len(texts2)):]
testY = labels2[int(0.8*len(labels2)):]
#exit(3)
def RandomForest(train,trainY,test,testY):
    text_clf = Pipeline([('vect', CountVectorizer()),
                      ('tfidf', TfidfTransformer()),
                      ('clf', RandomForestClassifier()),
    ])

    text_clf.fit(train,trainY)
    pickle.dump(text_clf, open("RandomForestSummarizer.pl", 'wb'))

    predictions = text_clf.predict(test)

    print(classification_report(testY,predictions))
    new_confusion_matrix = sklearn.metrics.confusion_matrix(predictions, testY)
    # self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
    # self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
    print(new_confusion_matrix)
    #pickle.dump(text_clf,open("RandomForestSummarizer.pkl","wb"))


RandomForest(train,trainY,test,testY)

class UniversalNNClassifier():
    def __init__(self):
        os.environ['PYTHONHASHSEED'] = '4'
        np.random.seed(523)
        self.max_words = 2000000
        self.batch_size = 64
        self.epochs = 50
        self.GLOVE_DIR = "../../Helpers/BratDataProcessing/Glove_dir"
        self.MAX_SEQUENCE_LENGTH = 100
        self.EMBEDDING_DIM = 300
        pass

    def train_CNN_words_only(self,X_train,y_train):
        embeddings_index = {}
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.tokenizer.fit_on_texts(X_train)
        sequences = self.tokenizer.texts_to_sequences(X_train)

        word_index = self.tokenizer.word_index
        f = open(os.path.join(self.GLOVE_DIR, 'glove.840B.300d.txt'))
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
                                    trainable=True)


        early_stopping = EarlyStopping(monitor='val_loss', patience=5)
        y_train = to_categorical(y_train)
        model = Sequential()
        model.add(embedding_layer)
        #model.add(Bidirectional(LSTM(100,activation='relu',return_sequences=True)))
        model.add(Conv1D(512, 5, activation='relu'))
        model.add(MaxPooling1D(20))
        model.add(Dropout(0.5))
        model.add(Conv1D(256, 4, activation='relu'))
        model.add(MaxPooling1D(1))
        model.add(Dropout(0.4))
        model.add(Flatten())
        #model.add(Dense(20,activation='relu'))
        model.add(Dense(2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='nadam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit(data, y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=1,
                                validation_split=0.1,
                                callbacks=[early_stopping]
                                )
        self.clf = model

    def save_CNN_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.tokenizer, open(path + "/tokenizer_binary.pck", 'wb'))
        model_json = self.clf.to_json()
        with open(path+"/model_binary.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.clf.save_weights(path+"/model_binary.h5")
        print("Model saved")

    def load_CNN_model(self,path):
        json_file = open(path+"/model_binary.json", 'r')
        loaded_model_json = json_file.read()
        self.tokenizer = pickle.load(open(path + "/tokenizer_binary.pck", 'rb'))
        json_file.close()
        self.clf = model_from_json(loaded_model_json)
        # load weights into new model
        self.clf.load_weights(path+"/model_binary.h5")
        return self


    def predict_CNN(self,X_test):
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

# cnn = UniversalNNClassifier()
# cnn.train_CNN_words_only(train,trainY)
# cnn.save_CNN_model('Models')
# pred = cnn.predict_CNN(test)
# cnn.print_reports(pred,testY)