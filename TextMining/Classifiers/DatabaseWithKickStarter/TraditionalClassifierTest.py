from nltk.corpus import stopwords
from sklearn.cross_validation import train_test_split
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

from TextMining.Classifiers.DatabaseWithKickStarter.text_cleaner import clean_text
from database_access import *

stemmer = EnglishStemmer()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
analyzer = CountVectorizer().build_analyzer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()

sql = '(SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%Kick%") limit 620)union (SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%ManualAnnotation%"))'
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
    projectList.append((text,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))


df = pd.DataFrame({'text':text_array,'classa':classa})

# df_majority = df[df.classa==1]
# df_minority = df[df.classa==0]
# df_minority_upsampled = resample(df_minority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=300,    # to match majority class
#                                  random_state=83293) # reproducible results
df_upsampled = df
# print df_upsampled
# exit()
print "New dataset"
# Display new class counts
print df_upsampled.classa.value_counts()

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()
#print df_upsampled

# train = text_array[0:int(0.8*len(text_array))]
# train_Y = innovativeness[0:int(0.8*len(actors))]
#
# test = text_array[int(0.8*len(text_array)):]
# test_Y = innovativeness[int(0.8*len(actors)):]

#categories = ['non actor', 'actor']
stopWords = set(stopwords.words('english'))
# text_clf = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
#                       ('tfidf', TfidfTransformer()),
#                       ('clf', MultinomialNB()),
#  ])
text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])


from sklearn import metrics
X,X_test,Y,Y_test = train_test_split(df_upsampled['text'],df_upsampled['classa'],test_size=0.2,random_state=42)
text_clf.fit(X,Y)
y_preds = text_clf.predict(X_test)

print(metrics.confusion_matrix(Y_test, y_preds))

print(metrics.classification_report(Y_test, y_preds))

# scores = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='f1')
# final = 0
# for score in scores:
#     final = final + score
# print scores
# print "F1 Final:" + str(final/10)
#
#
# scores1 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='precision')
# final = 0
# print "Precision"
# for score in scores1:
#     final = final + score
# print scores1
# print "Precision Final:" + str(final/10)
#
# scores2 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='recall')
# final = 0
# print "Recall"
# for score in scores2:
#     final = final + score
# print scores2
# print "Recall Final:" + str(final/10)
