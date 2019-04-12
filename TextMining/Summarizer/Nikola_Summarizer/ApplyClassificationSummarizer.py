#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import pickle

from pymongo import MongoClient

from TextMining.database_access import *
import nltk
from langdetect import detect

text_clf = pickle.load(open("NaiveBayesSummarizer.sav", 'rb'))

def make_summary(text):
    text = text.replace("'"," ")
    sents = nltk.sent_tokenize(text)
    predictions = text_clf.predict(sents)
    summary = ""
    for i in range(0, len(predictions)):
        if predictions[i] == 1:
            summary = summary + " " + sents[i].encode("utf-8",errors='replace')
            if len(summary)>10000:
                return summary

    return summary
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

    try:
        desc_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%desc%' and Projects_idProjects="+str(idProject);
        cursor.execute(desc_sql)
        results2 = cursor.fetchall()
        projectText = ""
        page_at = "Description"
        for r2 in results2:
            text = r2[2]
            projectText = projectText + " " + text
        if len(projectText)>1500:
            sum = make_summary(projectText)
            if len(sum) > 2:
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(sum,idProject)
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
            sum = make_summary(projectText)
            if len(sum) > 2:
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(sum,idProject)
                cursor.execute(sql)
                db.commit()
            continue
        elif len(projectText) > 300:
            sum = make_summary(projectText)
            if len(sum) > 2:
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(sum,idProject)
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
                sum = make_summary(projectText)
                if len(sum) > 2:
                    sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(
                        sum, idProject)
                    cursor.execute(sql)
                    db.commit()
                continue
            elif len(projectText) > 300:
                sum = make_summary(projectText)
                if len(sum) > 2:
                    sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(
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
                    sum = make_summary(projectText)
                    if len(sum) > 2:
                        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(
                            sum, idProject)
                        cursor.execute(sql)
                        db.commit()
                    continue
                elif len(projectText) > 300:
                    sum = make_summary(projectText)
                    if len(sum) > 2:
                        sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(
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
            sum = make_summary(projectText)
            if len(sum) > 2:
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(sum,idProject)
                cursor.execute(sql)
                db.commit()
            continue
        elif len(projectText) > 300:
            sum = make_summary(projectText)
            if len(sum) > 2:
                sql = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('Description_sum','{0}',{1},NOW(),'NB Summarizer v2')".format(sum,idProject)
                cursor.execute(sql)
                db.commit()
            continue
    except:
        print("Error:"+str(idProject))

