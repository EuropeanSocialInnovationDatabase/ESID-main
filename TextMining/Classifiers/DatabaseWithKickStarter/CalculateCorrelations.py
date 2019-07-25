from nltk.corpus import stopwords
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
import matplotlib.pyplot as plt
import imgkit

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
objectives = []
actors = []
outputs = []
innovativeness = []
social_innovation = []
project_id = []
for res in results:
    Outputs = res[1]
    if Outputs>1:
        bin_Outputs = 1
    else:
        bin_Outputs = 0
    Objectives = res[2]
    if Objectives>1:
        binObjectives = 1
    else:
        binObjectives = 0
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
    project_id.append(projectId)
    objectives.append(binObjectives)
    actors.append(binActors)
    outputs.append(bin_Outputs)
    innovativeness.append(binInnovativeness)
    social_innovation.append(bin_SocialInnovation)
    projectList.append((text,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))
df = pd.DataFrame({'objectives':objectives,'actors':actors,'outputs':outputs,'innovativeness':innovativeness,'social_innovation':social_innovation})
corr = df.corr()
rend = corr.style.background_gradient(cmap='coolwarm').render()
f = open("correnlation.html","w")
f.write(rend)
f.close()
print(df.describe())