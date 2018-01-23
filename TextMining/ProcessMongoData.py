#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
from NER.StanfordNER import StanfordTagger
import requests
import json

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
        if project_text == "":
            continue
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




