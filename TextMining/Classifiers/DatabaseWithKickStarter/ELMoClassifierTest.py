from keras import Input, Model
from keras.layers import Lambda, Dense, Conv1D, MaxPooling1D, Flatten
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.utils import resample, shuffle
from sklearn.model_selection import cross_val_score
from pymongo import MongoClient
from nltk.stem.snowball import EnglishStemmer
import tensorflow as tf
import tensorflow_hub as hub
from sklearn import preprocessing
import keras
import numpy as np
from sklearn import metrics

import MySQLdb
from database_access import *

stemmer = EnglishStemmer()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
analyzer = CountVectorizer().build_analyzer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()

sql = '(SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%Kick%") limit 800)union (SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%ManualAnnotation%"))'
cursor.execute(sql)
results = cursor.fetchall()
projectList = []
text_array = []
classa = []
objectives = []
outputs = []
innovativeness = []
for res in results:
    Outputs = res[1]
    if Outputs>1:
        bin_Outputs = 1
    else:
        bin_Outputs = 0
    Objectives = res[2]
    if Objectives>1:
        binObjectives = "Pos"
    else:
        binObjectives = "Neg"
    Actors = res[3]
    if Actors>1:
        binActors = 1
    else:
        binActors = 0
    Innovativeness = res[4]
    if Innovativeness>1:
        binInnovativeness =1
    else:
        binInnovativeness = 0
    projectId = res[5]
    SocialInnovation = res[6]
    if SocialInnovation == None:
        continue
    if SocialInnovation>1:
        bin_SocialInnovation = 1
    else:
        bin_SocialInnovation = 0
    des_sql = 'SELECT * FROM EDSI.AdditionalProjectData where FieldName like "%Desc%" and Projects_idProjects='+str(projectId)
    cursor.execute(des_sql)
    results2 = cursor.fetchall()
    text = ""
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(projectId)},
                                            no_cursor_timeout=True).batch_size(100)
    for res2 in results2:
        text = text + " "+res2[2]
    for doc in documents:
        text = text + " "+ doc['translation']
    text_array.append(text[0:3000])
    classa.append(binActors)
    objectives.append(binObjectives)
    outputs.append(bin_Outputs)
    innovativeness.append(binInnovativeness)
    projectList.append((text,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))


df = pd.DataFrame({'text':text_array,'classa':classa})

#resample(df_minority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=300,    # to match majority class
#                                  random_state=83293) # reproducible results

df_upsampled = df
# print df_upsampled
# exit()
print("New dataset")
# Display new class counts
print(df_upsampled.classa.value_counts())

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()
le = preprocessing.LabelEncoder()
le.fit(classa)
def encode(le, labels):
    enc = le.transform(labels)
    return keras.utils.to_categorical(enc)

def decode(le, one_hot):
    dec = np.argmax(one_hot, axis=1)
    return le.inverse_transform(dec)
#X,X_test,Y,Y_test = train_test_split(text_array,classa,test_size=0.2,random_state=42)
x_enc = df_upsampled['text']
y_enc = encode(le, df_upsampled['classa'])

x_train = np.asarray(x_enc[:1300])
y_train = np.asarray(y_enc[:1300])

x_test = np.asarray(x_enc[1300:])
y_test = np.asarray(y_enc[1300:])

from keras.layers import Input, Lambda, Dense
from keras.models import Model
url = "https://tfhub.dev/google/elmo/2"
embed = hub.Module(url)
import keras.backend as K

def ELMoEmbedding(x):
    return tf.expand_dims(embed(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"], axis=-1)

input_text = Input(shape=(1,), dtype=tf.string)
embedding = Lambda(ELMoEmbedding, output_shape=(1024,1, ))(input_text)
#dense = Dense(256, activation='relu')(embedding)
conv = Conv1D(256, 5, activation='relu',input_shape=(1024,1,1))(embedding)
pool = MaxPooling1D(20)(conv)
conv2 = Conv1D(128, 5, activation='relu')(pool)
pool2 = MaxPooling1D(20)(conv2)
flat = Flatten()(pool2)
pred = Dense(2, activation='softmax')(flat)
model = Model(inputs=[input_text], outputs=pred)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

with tf.Session() as session:
    K.set_session(session)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    history = model.fit(x_train, y_train, epochs=5, batch_size=4)
    model.save_weights('./elmo-model.h5')

with tf.Session() as session:
    K.set_session(session)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    model.load_weights('./elmo-model.h5')
    predicts = model.predict(x_test, batch_size=32)

y_test = decode(le, y_test)
y_preds = decode(le, predicts)

from sklearn import metrics

print(metrics.confusion_matrix(y_test, y_preds))

print(metrics.classification_report(y_test, y_preds))
