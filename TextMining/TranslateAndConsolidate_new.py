#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
import time
from database_access import *
from langdetect import detect
from mtranslate import translate
from nltk.metrics.distance import edit_distance
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Project:
    def __init__(self):
        self.name = ""
        self.webpage = ""
        self.first_datasource = ""
        self.first_datasource_id = -1
        self.idProject = -1

def find_org(org,tokens):
    org_tokens = nltk.word_tokenize(org)
    l_org_tokens = len(org_tokens)
    for i in range(0,len(tokens)-l_org_tokens+1):
        pot = tokens[i:(i+l_org_tokens)]
        pot_s = ' '.join(pot)
        distance = edit_distance(pot_s.lower(),org.lower())
        if float(distance)/float(len(org))<0.1:
            return True
    return False

if __name__ == '__main__':
    print("Initializing")
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    print("Selecting projects from mysql")
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where Exclude=0 and idProjects>2083"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    print("Initializing Mongo")
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    translationTimeout = 0

    for res in results:
        #project_names.append(res[0])
        print("Reading project "+str(res[0]) )
        number_of_pages = 0
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        print(pro.idProject)
        project_list.append(pro)
        print("Grabbing documents from Mongo")
        documents = mongo_db.crawl20180801.find({"mysql_databaseID":str(pro.idProject),"page_title":{"$regex":"(A|a)bout|(V|v)ision|(M|m)ision|(C|c)ontact|(K|k)ontakt|(P|p)artner"}},no_cursor_timeout=True).batch_size(100)
        project_text = ""
        original_text = ""
        if documents.count()==0:
            print("Too few documents")
            documents = mongo_db.crawl20180801.find({"mysql_databaseID": str(pro.idProject)},
                                                       no_cursor_timeout=True).batch_size(100)
        print("Making a big document")

        for doc in documents:
            number_of_pages = number_of_pages + 1
            project_text = project_text +  doc["page_title"]
            project_text = project_text + "\n===============================\n\n"
            project_text = project_text + doc["text"]

        print("Language detection")
        if project_text == "":
            language = 'en'
        else:
            try:
                language = detect(project_text)
            except:
                continue
        original_text = project_text

        print "Language:"+str(language)
        if language!="en":
            print("Start translating")
            tokens = nltk.word_tokenize(project_text)
            i = 0
            text_to_translate = ""
            translated = ""
            while i < len(tokens):
                for j in range(0,100):
                    if i>=len(tokens):
                        continue
                    text_to_translate = text_to_translate + " "+tokens[i]
                    i= i + 1
                try:
                    en_text = translate(text_to_translate.encode('utf-8').strip(),"en","auto")
                except:
                    print "Timeout translation"
                    translationTimeout = translationTimeout + 1
                translated = translated +" "+ en_text
                text_to_translate = ""
            print translated
            project_text = translated
            print("End translating")

        project_text = project_text.encode('utf-8').strip()
        print("Grabbing descriptions")
        sql_desc = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(pro.idProject)
        cursor.execute(sql_desc)
        f_desc = cursor.fetchall()
        print("Appending descriptions")
        description_len = 0
        description_pages = 0
        for d in f_desc:
            project_text = project_text+ " \n\n "+d[2].encode('utf-8').strip()
            original_text = original_text+ " \n\n "+d[2].encode('utf-8').strip()
            description_pages = description_pages + 1
            description_len = description_len + len(d[2].encode('utf-8').strip())
        if project_text == "":
            print("No text on site and in database")
            #Make all predictions 0
            db.commit()
            continue
        try:
            mongo_db.crawl20180801_translated.insert_one(
                {
                    "timestamp":time.time(),
                    "relatedTo": "Projects",
                    "mysql_databaseID": str(pro.idProject),
                    "name": pro.name,
                    "url": pro.webpage,
                    #"text": original_text,
                    "translation": project_text,
                    "translationLen":int(str(len(project_text))),
                    "NumberOfCrawledPages":int(str(number_of_pages)),
                    "DescriptionPages":int(str(description_pages)),
                    "DescriptionLength":int(str(description_len)),
                    "DescriptionLength2": int(description_len),
                    "translationLen2": int(len(project_text)),
                    "Language":language
                })
        except:
            print("Error - file too large"+str(pro.idProject))
    print "Translation timeouts on: "+str(translationTimeout)+" pages"

