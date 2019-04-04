#!/usr/bin/python
# -*- coding: utf-8 -*-
from joblib import load
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer

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
    for i in range(0,len(sum)):
        whole_txt = sum.extend(orig)
        tfidf = TfidfVectorizer(stop_words='english').fit(whole_txt)
        sum_sents = nltk.sent_tokenize(sum)
        orig_sents = nltk.sent_tokenize(orig)
        for ss in sum_sents:
            for os in orig_sents:
                tfidf_scores = tfidf.transform([ss,os])
                cos_sim = ((tfidf_scores * tfidf_scores.T).A)[0,1]
                if cos_sim>0.8:
                    positive.append(os)
                else:
                    negative.append(os)
    return positive,negative



mySQLSummaries,mongo_original = collect_data()
positive,negative = tf_idf_classify_sentences(mySQLSummaries,mongo_original)
print(positive)