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

class Project:
    def __init__(self):
        self.name = ""
        self.webpage = ""
        self.first_datasource = ""
        self.first_datasource_id = -1
        self.idProject = -1

if __name__ == '__main__':
    project_names = []
    actor_names = []
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_actors = "Select ActorName from Actors"
    cursor.execute(sql_actors)
    results = cursor.fetchall()
    for res in results:
        actor_names.append(res[0])
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects limit 10"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    st = StanfordTagger()
    for res in results:
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
                en_text = translate(text_to_translate,"en","auto")
                translated = translated +" "+ en_text
                text_to_translate = ""
            print translated
        classified_text = st.tag_text(project_text)
        print(classified_text)
        extracted_locations = []
        extracted_orgs = []
        loc_full_name = ""
        org_full_name = ""
        was_prev_loc = False
        was_prev_org = False
        for t in classified_text:
            if t[1]=="LOCATION":
                if was_prev_loc == False:
                    loc_full_name = loc_full_name +" "+ t[0]
                    was_prev_loc = True
                    continue
                if was_prev_loc == True:
                    loc_full_name = loc_full_name + " "+t[0]
            if t[1]!= "LOCATION":
                if was_prev_loc:
                    extracted_locations.append(loc_full_name)
                    loc_full_name = ""
                was_prev_loc = False
            if t[1]=="ORGANIZATION":
                if was_prev_org == False:
                    org_full_name = org_full_name +" "+t[0]
                    was_prev_org = True
                    continue
                if was_prev_org == True:
                    org_full_name = org_full_name +" "+t[0]
            if t[1]!= "ORGANIZATION":
                if was_prev_org:
                    extracted_orgs.append(org_full_name)
                    org_full_name = ""
                was_prev_org = False
        print extracted_orgs
        print "-----------"
        print extracted_locations

        r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data=project_text.encode('utf-8').strip())
        print(r.status_code, r.reason)
        print(r.text)
        if "Error" in r.text :
            continue
        data = json.loads(r.text)
        for clas in data["classification"]:
            print "Class:" + clas + ":" + str(data["classification"][clas]["score"])
            print "Keywords"
            for key in data["classification"][clas]["keywords"]:
                print key + ":" + str(data["classification"][clas]["keywords"][key])




