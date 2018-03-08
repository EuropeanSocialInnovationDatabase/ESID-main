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
                if "DOCTYPE" in line:
                    continue
                if len(line)<10:
                    continue
                tokens = nltk.word_tokenize(line)
                if len(tokens)<5:
                    continue
                if line in project_document_lines:
                    continue
                project_document_lines.add(line)
                new_doc_text = new_doc_text+'\n'+line

            if pro.name in doc["text"]:
                description = description+doc["text"]

            project_text = project_text + "\n"+ doc["page_title"]
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
            lines = project_text.split('\n')
            for line in lines:
                if len(line)>500:
                    while i<len(tokens):
                        for j in range(0, 100):
                            if i >= len(tokens):
                                continue
                            text_to_translate = text_to_translate +  " " + tokens[i]
                            i = i + 1
                        en_text = translate(text_to_translate.encode('utf-8'), "en", "auto")
                        translated = translated + "\n" + en_text
                        text_to_translate = ""
                else:
                    en_text = translate(line.encode('utf-8'), "en", "auto")
                    translated = translated + "\n" + en_text
            project_text = translated
            # while i < len(tokens):
            #     for j in range(0, 100):
            #         if i >= len(tokens):
            #             continue
            #         text_to_translate = text_to_translate + " " + tokens[i]
            #         i = i + 1
            #     en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
            #     translated = translated + " " + en_text
            #     text_to_translate = ""
            # print translated
            # project_text = translated


        project_text = project_text.encode('utf-8').strip()
        txt = open("Cleaned_text/"+pro.name.replace(' ','_')+".txt",'w')
        txt.write(project_text)
        txt.close()
        txt2 = open("Cleaned_Desc/" + pro.name.replace(' ','_') + ".txt", 'w')
        txt2.write(description)
        txt2.close()
