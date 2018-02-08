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
import os

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

    project_names = []
    actor_names = []
    orglist_names = []

    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        f_gate = open("AllPros/p_"+res[0].replace('/','')+".txt",'w')
        project_names.append(res[0])
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        documents = mongo_db.projects_actors2.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(30)
        project_text = ""
        for doc in documents:
            project_text = project_text +  doc["page_title"]
            project_text = project_text + "\n===============================\n\n"
            project_text = project_text + doc["text"]
        if project_text == "":
            f_gate.close()
            os.remove("AllPros/p_"+res[0].replace('/','')+".txt")
            continue
        language = detect(project_text)
        print "Language:"+str(language)
        if language!="en":
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
                en_text = translate(text_to_translate.encode('utf-8').strip(),"en","auto")
                translated = translated +" "+ en_text
                text_to_translate = ""
            print translated
            project_text = translated

        project_text = project_text.encode('utf-8').strip()
        f_gate.write(project_text)
        f_gate.close()