#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
from NER.StanfordNER import StanfordTagger
import requests
import json
from langdetect import detect
from mtranslate import translate
import csv
from nltk.metrics.distance import edit_distance
import pickle
from commonregex import CommonRegex
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

if __name__ == '__main__':
    print("Initializing")
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    print("Selecting projects from mysql")
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where DataSources_idDataSources=56;"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    print("Initializing Mongo")
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    for res in results:
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        print("Grabbing documents from Mongo")
        documents = mongo_db.SI_drive.find({"mysql_databaseID": str(pro.idProject)},
                                                   no_cursor_timeout=True).batch_size(100)
        project_text = ""
        original_text = ""
        description = ""
        if documents.count() > 1000:
            print("Too many documents")
            documents = mongo_db.SI_drive.find(
                {"mysql_databaseID": str(pro.idProject), "page_title": {"$regex": "about"}},
                no_cursor_timeout=True).batch_size(100)
        print("Making a big document")
        project_document_lines = set()
        extracted_locations = []
        extracted_orgs = []
        for doc in documents:
            split_lines = doc["text"].split('\n')
            new_doc_text = ""
            for line in split_lines:
                if len(line)<10:
                    continue
                tokens = nltk.word_tokenize(line)
                if tokens<5:
                    continue
                if line in project_document_lines:
                    continue
                project_document_lines.add(line)
                new_doc_text = new_doc_text+'\n'+line

            if pro.name in doc["text"]:
                description = description+doc["text"]

            project_text = project_text + doc["page_title"]
            project_text = project_text + "\n===============================\n\n"
            project_text = project_text + new_doc_text

            original_text = project_text

            if project_text == "":
                continue
            language = detect(project_text)
            print "Language:" + str(language)
            if language != "en":
                tokens = nltk.word_tokenize(project_text)
                tokens2 = nltk.word_tokenize(description)
                i = 0
                text_to_translate = ""
                translated = ""
                while i < len(tokens):
                    for j in range(0, 100):
                        if i >= len(tokens):
                            continue
                        text_to_translate = text_to_translate + " " + tokens[i]
                        i = i + 1
                    en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
                    translated = translated + " " + en_text
                    text_to_translate = ""
                print translated
                project_text = translated

                i = 0
                text_to_translate = ""
                translated = ""
                while i < len(tokens2):
                    for j in range(0, 100):
                        if i >= len(tokens2):
                            continue
                        text_to_translate = text_to_translate + " " + tokens2[i]
                        i = i + 1
                    en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
                    translated = translated + " " + en_text
                    text_to_translate = ""
                description = translated

            project_text = project_text.encode('utf-8').strip()
            st = StanfordTagger('Resources')
            short_texts = project_text.splitlines()
            classified_text = []
            for t in short_texts:
                classified_text = classified_text + st.tag_text(t)
            st = None


            print(classified_text)
            loc_full_name = ""
            org_full_name = ""
            was_prev_loc = False
            was_prev_org = False
            for t in classified_text:
                if t[1] == "LOCATION":
                    if was_prev_loc == False:
                        loc_full_name = loc_full_name + " " + t[0]
                        was_prev_loc = True
                        continue
                    if was_prev_loc == True:
                        loc_full_name = loc_full_name + " " + t[0]
                if t[1] != "LOCATION":
                    if was_prev_loc:
                        extracted_locations.append(loc_full_name)
                        loc_full_name = ""
                    was_prev_loc = False
                if t[1] == "ORGANIZATION":
                    if was_prev_org == False:
                        org_full_name = org_full_name + " " + t[0]
                        was_prev_org = True
                        continue
                    if was_prev_org == True:
                        org_full_name = org_full_name + " " + t[0]
                if t[1] != "ORGANIZATION":
                    if was_prev_org:
                        extracted_orgs.append(org_full_name)
                        org_full_name = ""
                    was_prev_org = False
        mongo_db.SI_drive2.insert_one(
            {
                "relatedTo": "Project",
                "mysql_databaseID": str(pro.idProject),
                "name": pro.name,
                "start_url": pro.webpage,
                "original_text": original_text,
                "translated_text": project_text,
                "description":description,
                "organisations": str(extracted_orgs),
                "locations":str(extracted_locations)
            }

        )
