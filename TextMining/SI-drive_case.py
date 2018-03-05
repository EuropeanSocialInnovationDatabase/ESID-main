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
        if documents.count() > 1000:
            print("Too many documents")
            documents = mongo_db.SI_drive.find(
                {"mysql_databaseID": str(pro.idProject), "page_title": {"$regex": "about"}},
                no_cursor_timeout=True).batch_size(100)
        print("Making a big document")
        project_document_lines = set()
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

            project_text = project_text + doc["page_title"]
            project_text = project_text + "\n===============================\n\n"
            project_text = project_text + new_doc_text