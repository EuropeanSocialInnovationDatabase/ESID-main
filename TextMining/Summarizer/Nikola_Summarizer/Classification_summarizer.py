#!/usr/bin/python
# -*- coding: utf-8 -*-
from joblib import load
import numpy as np
import json

from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
import pickle

from TextMining.database_access import *
import MySQLdb
from pymongo import MongoClient
from langdetect import detect
from mtranslate import translate
import nltk
import signal
translationTimeout = 0
def handler(signum, frame):
    print("Forever is over!")
    raise Exception("end of time")
def checkEngAndTranslate(project_text):
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(60)
    global translationTimeout
    language = 'en'
    if project_text == "":
        language = 'en'
    else:
        try:
            language = detect(project_text)
        except:
            print("Error translating")
    print("Language:" + str(language))
    if language == "en":
        return project_text
    if language != "en":
        return ""
        print("Start translating")
        tokens = nltk.word_tokenize(project_text)
        i = 0
        text_to_translate = ""
        translated = ""
        while i < len(tokens):
            for j in range(0, 200):
                if i >= len(tokens):
                    continue
                text_to_translate = text_to_translate + " " + tokens[i]
                i = i + 1
            try:
                en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
            except:
                print("Timeout translation")
                translationTimeout = translationTimeout + 1
                en_text  = ""
            translated = translated + " " + en_text
            text_to_translate = ""
        print(translated)
        project_text = translated
        print("End translating")
        return project_text
    return project_text

def collect_data():
    descriptions = []
    original_texts = []
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
    db.set_character_set("utf8")
    db2.set_character_set("utf8")
    cursor = db.cursor()
    sql_projects = "SELECT idProjects,ProjectName, Value FROM EDSI.Projects left join AdditionalProjectData on idProjects= Projects_idProjects where Exclude = 0 and FieldName like '%Desc%' and FieldName not like '%_sum%' and char_length(Value)>400"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient(unicode_decode_error_handler='ignore')
    mongo_db = mongo_client.ESID
    for row in results:
        idProject = row[0]
        print("Project ID:" + str(idProject))
        projectName = row[1]
        description = row[2]
        documents = mongo_db.crawl20190109.find(
            {"mysql_databaseID": str(idProject)},
            no_cursor_timeout=True).batch_size(100)
        full_text = ""
        for doc in documents:
            full_text = full_text + " "+doc['text']
        projectText = checkEngAndTranslate(full_text)
        descriptions.append(description)
        original_texts.append(projectText)
    y = json.dumps(descriptions)
    z = json.dumps(original_texts)
    f = open("descriptions.json", "w")
    f.write(y)
    f.close()
    f = open("original_texts.json", "w")
    f.write(z)
    f.close()

    return descriptions,original_texts

def tf_idf_classify_sentences(sum,orig):
    positive = []
    negative = []
    max_cos = 0
    whole_txt = sum+orig
    tfidf = TfidfVectorizer(stop_words='english').fit(whole_txt)
    for i in range(0,len(sum)):
        sum_sents = nltk.sent_tokenize(sum[i])
        orig_sents = nltk.sent_tokenize(orig[i])
        for ss in sum_sents:
            for os in orig_sents:
                tfidf_scores = tfidf.transform([ss,os])
                cos_sim = ((tfidf_scores * tfidf_scores.T).A)[0,1]
                if cos_sim>max_cos:
                    max_cos = cos_sim
                if cos_sim>0.35:
                    positive.append(os)
                else:
                    negative.append(os)
                if len(positive)>30000:
                    return positive,negative
    return positive,negative



#mySQLSummaries,mongo_original = collect_data()
# with open('descriptions.json') as f:
#     mySQLSummaries = json.load(f)
# with open('original_texts.json') as f:
#     mongo_original = json.load(f)
# positive,negative = tf_idf_classify_sentences(mySQLSummaries,mongo_original)
# y = json.dumps(positive)
# z = json.dumps(negative)
# f = open("positive.json", "w")
# f.write(y)
# f.close()
# f = open("negative.json", "w")
# f.write(z)
# f.close()
# exit(5)
with open('positive.json') as f:
    positive = json.load(f)
with open('negative.json') as f:
    negative = json.load(f)

print(len(positive))
print(len(negative))
dataset = []
for pos in positive:
    dataset.append([pos,1])
i = 0
while i <10000:
    dataset.append([negative[i],0])
    i = i+1
data = DataFrame.from_records(dataset)
data = data.sample(frac=1).reset_index(drop=True)
X_train, X_test, y_train, y_test = train_test_split(data[0], data[1], test_size=0.2, random_state=432)
text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()), ])

text_clf.fit(X_train, y_train)

y_pred = text_clf.predict(X_test)
print(metrics.classification_report(y_test, y_pred))

print(metrics.confusion_matrix(y_test, y_pred))

pickle.dump(text_clf,open("NaiveBayesSummarizer.sav", 'wb'))

text_clf = None

text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()), ])

text_clf = pickle.load(open("NaiveBayesSummarizer.sav", 'rb'))

y_pred = text_clf.predict(X_test)
print(metrics.classification_report(y_test, y_pred))

print(metrics.confusion_matrix(y_test, y_pred))
