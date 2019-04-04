#!/usr/bin/python
# -*- coding: utf-8 -*-
from joblib import load
import numpy as np
from preprocess import preprocess_text
from TextMining.database_access import *
import MySQLdb
from pymongo import MongoClient
from langdetect import detect
from mtranslate import translate
import nltk
import signal
import pandas as pd
from stemmed_vectorizer import StemmedCountVectorizer

# parser = argparse.ArgumentParser(description='SVM Summarizer')
# parser.add_argument('-type', type=int, default=1)
# parser.add_argument('-output', type=str, default='output.json')
# parser.add_argument('-input', type=str, default='input.json')
# parser.add_argument('-sents_per_topic', type=int, default=2)
# args = parser.parse_args()
def handler(signum, frame):
    print("Forever is over!")
    raise Exception("end of time")
MODEL_FOLDER = 'Models/'
SPLIT_TOKEN = '\n'
SENTS_PER_TOPIC = 2 #args.sents_per_topic
translationTimeout = 0
def checkEngAndTranslate(project_text):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)
    global translationTimeout
    language = 'en'
    if project_text == "":
        language = 'en'
    else:
        try:
            language = detect(project_text)
        except:
            print("Error translating")
    original_text = project_text
    print("Language:" + str(language))
    if language == "en":
        return project_text
    if language != "en":
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
def extract_summary(predicted, all_sents):
    summary = list()
    for index, predict in enumerate(predicted):
        if int(predict) == 1:
            summary.append(all_sents[index])
    return ' '.join(summary)

def get_binary_summary(text):
    svm = load(MODEL_FOLDER + 'binary_svm.joblib')
    sents = text.split(SPLIT_TOKEN)
    predicted = svm.predict(sents)
    return extract_summary(predicted, sents)

def convert_to_labels(sent_probs):
    probs = sent_probs.copy()
    probs[::-1].sort()
    for index, prob in enumerate(sent_probs):
        if prob in probs[:SENTS_PER_TOPIC]:
            sent_probs[index] = 1
        else:
            sent_probs[index] = 0
    return sent_probs

def load_topic_models():
    objective_svm = load(MODEL_FOLDER + 'objective_svm.joblib')
    actor_svm = load(MODEL_FOLDER + 'actor_svm.joblib')
    innovation_svm = load(MODEL_FOLDER + 'innovation_svm.joblib')
    output_svm = load(MODEL_FOLDER + 'output_svm.joblib')
    return objective_svm, actor_svm, innovation_svm, output_svm

def get_topics_summary_by_prob(text):
    objective_svm, actor_svm, innovation_svm, output_svm = load_topic_models()
    sents = text.split(SPLIT_TOKEN)
    objectives = convert_to_labels(objective_svm.predict_proba(sents)[:, 1])
    actors = convert_to_labels(actor_svm.predict_proba(sents)[:, 1])
    innovations = convert_to_labels(innovation_svm.predict_proba(sents)[:, 1])
    outputs = convert_to_labels(output_svm.predict_proba(sents)[:, 1])

    predicted = np.logical_or(objectives, actors)
    predicted = np.logical_or(predicted, innovations)
    predicted = np.logical_or(predicted, outputs)

    return extract_summary(predicted, sents)


def get_topics_summary(text):
    objective_svm, actor_svm, innovation_svm, output_svm = load_topic_models()
    sents = text.split(SPLIT_TOKEN)

    objectives = objective_svm.predict(sents)
    actors = actor_svm.predict(sents)
    innovations = innovation_svm.predict(sents)
    outputs = output_svm.predict(sents)

    predicted = np.logical_or(objectives, actors)
    predicted = np.logical_or(predicted, innovations)
    predicted = np.logical_or(predicted, outputs)

    return extract_summary(predicted, sents)

def summarize(document):
    text = preprocess_text(document)
    # if args.type == 1:
    #     return get_binary_summary(text)
    # elif args.type == 2:
    #     return get_topics_summary(text)
    # else:
    return get_topics_summary_by_prob(text)

db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
db.set_character_set("utf8")
db2.set_character_set("utf8")
cursor = db.cursor()
cursor2 = db2.cursor()
sql_projects = "Select idProjects,ProjectName,ProjectWebpage from Projects  where Exclude = 0"
cursor.execute(sql_projects)
results = cursor.fetchall()
mongo_client = MongoClient(unicode_decode_error_handler='ignore')
mongo_db = mongo_client.ESID
for row in results:
    idProject = row[0]
    print("Project ID:"+str(idProject))
    projectName = row[1]
    projectWebpage = row[2]
    page_at = ""


    desc_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%desc%' and Projects_idProjects="+str(idProject);
    cursor.execute(desc_sql)
    results2 = cursor.fetchall()
    projectText = ""
    page_at = "Description"
    for r2 in results2:
        text = r2[2]
        projectText = projectText + " " + text
    if len(projectText)>1500:
        sum = summarize(projectText)
        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(sum,idProject)
        cursor.execute(sql)
        db.commit()
        continue

    documents = mongo_db.crawl20190109.find({"mysql_databaseID": str(idProject),"page_title":{"$regex":"([a|A]bout)"}}, no_cursor_timeout=True).batch_size(100)
    page_at = "About"
    projectText = ""
    for doc in documents:
        text = doc['text']
        projectText = projectText + " " + text
    projectText = checkEngAndTranslate(projectText)
    if len(projectText) > 1500:
        sum = summarize(projectText)
        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
            sum, idProject)
        cursor.execute(sql)
        db.commit()
        continue
    elif len(projectText) > 300:
        sum = summarize(projectText)
        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
            sum, idProject)
        cursor.execute(sql)
        db.commit()
        continue

    documents = mongo_db.crawl20190109.find(
        {"mysql_databaseID": str(idProject)},
        no_cursor_timeout=True).batch_size(100)
    projectText = ""
    if documents.count()<=2:
        page_at = "One page"
        for doc in documents:
            text = doc['text']
            projectText = projectText + " " + text
        projectText = checkEngAndTranslate(projectText)
        if len(projectText) > 1500:
            sum = summarize(projectText)
            sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
                sum, idProject)
            cursor.execute(sql)
            db.commit()
            continue
        elif len(projectText) > 300:
            sum = summarize(projectText)
            sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
                sum, idProject)
            cursor.execute(sql)
            db.commit()
            continue

    else:
        main_text = ""
        for doc in documents:
            if doc['url'].replace(" ","").lower() == projectWebpage.replace(" ","").lower():
                main_text = doc['text']
                page_at = "Main page"
            if main_text !="":
                break
        projectText = main_text
        if projectText !="":
            projectText = checkEngAndTranslate(projectText)
            if len(projectText) > 1500:
                sum = summarize(projectText)
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
                    sum, idProject)
                cursor.execute(sql)
                db.commit()
                continue
            elif len(projectText) > 300:
                sum = summarize(projectText)
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
                    sum, idProject)
                cursor.execute(sql)
                db.commit()
                continue
    projectText = ""
    for doc in documents:
        projectText = projectText + " "+doc["text"]
    page_at = "General"
    projectText = checkEngAndTranslate(projectText)
    if len(projectText) > 1500:
        sum = summarize(projectText)
        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI  SVMSummarizer v1')".format(
            sum, idProject)
        cursor.execute(sql)
        db.commit()
        continue
    elif len(projectText) > 300:
        sum = summarize(projectText)
        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'SI SVM Summarizer v1')".format(
            sum, idProject)
        cursor.execute(sql)
        db.commit()
        continue


# df = pd.read_json(args.input)
# df['summary'] = df.apply(lambda x: summarize(x.document), axis=1)
#
# with open(args.output, 'w') as f:
#     f.write(df.to_json(orient='records'))

# print('Summaries written to output file successfully!')