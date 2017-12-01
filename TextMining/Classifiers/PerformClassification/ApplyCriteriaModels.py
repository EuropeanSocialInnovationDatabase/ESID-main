# MLP for Pima Indians Dataset Serialize to JSON and HDF5
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy
from os import listdir
from os.path import isfile,join
import os
import sys
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding
sys.path.insert(0, '../Statistics/')
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

from Measures import *
max_words = 20000
batch_size = 32
MAX_SEQUENCE_LENGTH = 1100
json_file_actor = open('../Models/model_actors.json', 'r')
json_file_objectives = open('../Models/model_objectives.json', 'r')
json_file_outputs = open('../Models/model_outputs.json', 'r')
json_file_innovativeness = open('../Models/model_innovativeness.json', 'r')
loaded_model_actor_json = json_file_actor.read()
loaded_model_objectives_json = json_file_objectives.read()
loaded_model_outputs_json = json_file_outputs.read()
loaded_model_innovativeness_json = json_file_innovativeness.read()
json_file_actor.close()
json_file_objectives.close()
json_file_outputs.close()
json_file_innovativeness.close()
loaded_model_actor = model_from_json(loaded_model_actor_json)
loaded_model_objectives = model_from_json(loaded_model_objectives_json)
loaded_model_outputs = model_from_json(loaded_model_outputs_json)
loaded_model_innovativeness = model_from_json(loaded_model_innovativeness_json)
# load weights into new model
loaded_model_actor.load_weights("../Models/model_actors.h5")
loaded_model_objectives.load_weights("../Models/model_objectives.h5")
loaded_model_outputs.load_weights("../Models/model_outputs.h5")
loaded_model_innovativeness.load_weights("../Models/model_innovativeness.h5")
print("Loaded model from disk")
EMBEDDING_DIM = 50

# evaluate loaded model on test data
#loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
loaded_model_actor.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_objectives.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_outputs.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_innovativeness.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
data_folder = "../../../Helpers/FullDataset_Alina/Ann1"
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder,f))]

files = []
for file in onlyfiles:
    X= []
    if file.endswith("txt"):
        files.append(file)
        f = open(data_folder+"/"+file,"r")
        content = f.read()
        X.append(content)

        Y = [1,0]

        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(X)
        sequences = tokenizer.texts_to_sequences(X)

        word_index = tokenizer.word_index
        print('Found %s unique tokens.' % len(word_index))

        data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

        labels = to_categorical(np.asarray(Y))
        print('Shape of data tensor:', data.shape)
        print('Shape of label tensor:', labels.shape)

        # split the data into a training set and a validation set
        indices = np.arange(data.shape[0])
        data = data[indices]
        #labels = labels[indices]
        nb_validation_samples = int(0.1 * data.shape[0])
        # x_train = data
        # y_train = labels
        x_val = data
        #y_val = labels

        #early_stopping = EarlyStopping(monitor='val_loss', patience=15)
        print "Actor"
        predictions_actor = loaded_model_actor.predict(x_val,batch_size,1)
        i = 0
        for pred in predictions_actor:
            print str(file) +": "+str(pred)
            i = i+1
        print "Objectives"
        predictions_objectives = loaded_model_objectives.predict(x_val,batch_size,1)
        i = 0
        for pred in predictions_objectives:
            print str(file) + ": " + str(pred)
            i = i + 1
        print "Outputs"
        predictions_outputs = loaded_model_outputs.predict(x_val,batch_size,1)
        i = 0
        for pred in predictions_outputs:
            print str(file) + ": " + str(pred)
            i = i + 1
        print "Innovativeness"
        predictions_innovativeness = loaded_model_innovativeness.predict(x_val,batch_size,1)
        i = 0
        for pred in predictions_innovativeness:
            print str(file) + ": " + str(pred)
            i = i + 1
