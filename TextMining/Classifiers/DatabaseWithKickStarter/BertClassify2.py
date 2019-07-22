from keras.preprocessing.text import Tokenizer

from bert_embedding import BertEmbedding
from keras import Sequential
from keras.layers import Conv1D, MaxPooling1D, Dropout, Flatten, Dense, Activation, Embedding, Input
import numpy as np
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import resample, shuffle
from sklearn.model_selection import cross_val_score
from pymongo import MongoClient
import pickle
from nltk.stem.snowball import EnglishStemmer

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
    text_array.append(text)
    classa.append(binObjectives)
    projectList.append((text,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))


df = pd.DataFrame({'text':text_array,'classa':classa})

df_upsampled = df
# print df_upsampled
# exit()
print("New dataset")
# Display new class counts
print(df_upsampled.classa.value_counts())

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()
EMBEDDING_DIM = 1024
bert_embedding = BertEmbedding(model='bert_24_1024_16',dataset_name='book_corpus_wiki_en_cased')
X,X_test,Y,Y_test = train_test_split(text_array,classa,test_size=0.2,random_state=42)
tokenizer = Tokenizer(num_words=200000)
tokenizer.fit_on_texts(text_array)
word_index = tokenizer.word_index
embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    # if word =='\r' or word=='‎':
    #     continue
    embedding_vector = bert_embedding([word])
    if embedding_vector[0][1] == []:
        continue
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        #print(str(i)+": "+word)
        embedding_matrix[i] = embedding_vector[0][1][0].tolist()
    else:
        embedding_vector = bert_embedding(['the'])
        embedding_matrix[i] = embedding_vector[0][1][0].tolist()
embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=100,
                            trainable=True)
model = None
model = Sequential()
model.add(embedding_layer)
model.add(Conv1D(128,5,activation='relu'))
model.add(MaxPooling1D(20))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(1))
model.add(Activation('softmax'))

model.compile(loss='binary_crossentropy',
              optimizer='nadam',
              metrics=['accuracy'])
embeddings = bert_embedding(X)
X_embeds = pd.DataFrame(embeddings)

history = model.fit(X_embeds[1][0], Y,
                    batch_size=64,
                    epochs=10,
                    verbose=1,
                    validation_split=0.1,
                    )
predictions = model.predict(bert_embedding(X_test),64,1)
TP = Y_test*predictions
metrics.classification_report(bert_embedding(X_test), predictions,Y_test)