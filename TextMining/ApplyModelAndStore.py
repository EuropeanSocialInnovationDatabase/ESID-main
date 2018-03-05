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
    objectives_model = pickle.load(open('Classifiers/Models/naive_bayes_objectives.sav', 'rb'))
    actors_model = pickle.load(open('Classifiers/Models/naive_bayes_actors.sav', 'rb'))
    outputs_model = pickle.load(open('Classifiers/Models/naive_bayes_outputs.sav', 'rb'))
    innovativeness_model = pickle.load(open('Classifiers/Models/naive_bayes_innovativeness.sav', 'rb'))


    # project_names = []
    # actor_names = []
    # orglist_names = []
    # all_organisations = []

    # with open('Resources/org_gazzeteer.txt', 'rb') as csvfile:
    #     spamreader = csvfile.readlines()
    #     orglist_names = spamreader
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    # sql_actors = "Select ActorName from Actors"
    # cursor.execute(sql_actors)
    # results = cursor.fetchall()
    # for res in results:
    #     actor_names.append(res[0])
    # all_organisations = orglist_names
    # all_organisations.extend(actor_names)
    print("Selecting projects from mysql")
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where idProjects>7584 and idProjects<7676"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    print("Initializing Mongo")
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        #project_names.append(res[0])
        print("Reading project "+str(res[0]) )
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        print("Grabbing documents from Mongo")
        documents = mongo_db.projects_actors2.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(100)
        project_text = ""
        if documents.count()>1000:
            print("Too many documents")
            documents = mongo_db.projects_actors2.find({"mysql_databaseID": str(pro.idProject),"page_title":{"$regex":"about"}},
                                                       no_cursor_timeout=True).batch_size(100)
        print("Making a big document")

        for doc in documents:
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
                en_text = translate(text_to_translate.encode('utf-8').strip(),"en","auto")
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
        for d in f_desc:
            project_text = project_text+ " \n\n "+d[2].encode('utf-8').strip()
        if project_text == "":
            print("No text on site and in database")
            #Make all predictions 0
            sql_ins = "INSERT INTO EDSI.TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects) VALUES(%s,%s,%s,%s,%s)"
            cursor.execute(sql_ins ,
                           (0, 0, 0, 0, pro.idProject))
            db.commit()
            continue
        #common_regex_processed = CommonRegex(project_text)
        print("Making SI predictions")
        objective_pred = objectives_model.predict([project_text])
        objective_pred_v = 0
        if objective_pred==True:
            objective_pred_v = 1
        actor_pred = actors_model.predict([project_text])
        actor_pred_v = 0
        if actor_pred == True:
            actor_pred_v = 1
        outputs_pred = outputs_model.predict([project_text])
        outputs_pred_v = 0
        if outputs_pred == True:
            outputs_pred_v = 1
        innovativeness_pred = innovativeness_model.predict([project_text])
        innovativeness_pred_v = 0
        if innovativeness_pred == True:
            innovativeness_pred_v = 1
        print("Storing to database")
        project_text = project_text.decode('utf-8','ignore').strip()
        sql_ins = "INSERT INTO EDSI.TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects) VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(sql_ins,(outputs_pred_v,objective_pred_v,actor_pred_v,innovativeness_pred_v,pro.idProject))
        db.commit()

