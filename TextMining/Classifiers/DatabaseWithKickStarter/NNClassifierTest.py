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
from bert_text import run_on_dfs,make_features,create_tokenizer_from_hub_module
from nltk.stem.snowball import EnglishStemmer
import pprint
import tensorflow as tf
import bert
from bert import run_classifier

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
    text_array.append(text)
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
X,X_test,Y,Y_test = train_test_split(text_array,classa,test_size=0.2,random_state=42)

myparam = {
    "DATA_COLUMN": "text",
    "LABEL_COLUMN": "classa",
    "LEARNING_RATE": 2e-5,
    "NUM_TRAIN_EPOCHS": 20,
    "SAVE_SUMMARY_STEPS":100,
    "SAVE_CHECKPOINTS_STEPS":1500,
    #"bert_model_hub":"https://tfhub.dev/google/bert_uncased_L-24_H-1024_A-16"
}
df_train = pd.DataFrame({'text':X,'classa':Y})
df_test = pd.DataFrame({'text':X_test,'classa':Y_test})
resultAA, estimator,tokenizer = run_on_dfs(df_train, df_test, **myparam)
print(resultAA)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(resultAA)
for_prediction_input = pd.DataFrame({text:"This is a great project about making refugies finding their way in Germany. We provide them with services that they neeed",
                                     'classa':None})
test_features = make_features(for_prediction_input, [1,0], 128, tokenizer, 'text', 'classa')
test_input_fn = run_classifier.input_fn_builder(
        features=test_features,
        seq_length=128,
        is_training=False,
        drop_remainder=False)

n = estimator.predict(input_fn=test_input_fn, steps=None)
print(n)

