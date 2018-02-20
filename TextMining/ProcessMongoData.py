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
    output_file = open("output.txt",'w')
    objectives_model = pickle.load(open('Classifiers/Models/naive_bayes_objectives.sav', 'rb'))
    actors_model = pickle.load(open('Classifiers/Models/naive_bayes_actors.sav', 'rb'))
    outputs_model = pickle.load(open('Classifiers/Models/naive_bayes_outputs.sav', 'rb'))
    innovativeness_model = pickle.load(open('Classifiers/Models/naive_bayes_innovativeness.sav', 'rb'))


    project_names = []
    actor_names = []
    orglist_names = []
    all_organisations = []
    with open('Resources/org_gazzeteer.txt', 'rb') as csvfile:
        spamreader = csvfile.readlines()
        orglist_names = spamreader
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_actors = "Select ActorName from Actors"
    cursor.execute(sql_actors)
    results = cursor.fetchall()
    for res in results:
        actor_names.append(res[0])
    all_organisations = orglist_names
    all_organisations.extend(actor_names)
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects  limit 30,30"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        f_gate = open("Outputs/p_"+res[0]+".txt",'w')
        project_names.append(res[0])
        output_file.write("\n================================\n")
        output_file.write("Project name: "+res[0])
        output_file.write("\nWebpage: "+res[1])
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
                en_text = translate(text_to_translate.encode('utf-8').strip(),"en","auto")
                translated = translated +" "+ en_text
                text_to_translate = ""
            print translated
            project_text = translated

        project_text = project_text.encode('utf-8').strip()
        sql_desc = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(pro.idProject)
        cursor.execute(sql_desc)
        f_desc = cursor.fetchall()
        for d in f_desc:
            project_text = project_text+ " \n\n "+d[2].encode('utf-8').strip()
        common_regex_processed = CommonRegex(project_text)
        f_gate.write(project_text)
        objective_pred = objectives_model.predict([project_text])
        actor_pred = actors_model.predict([project_text])
        outputs_pred = outputs_model.predict([project_text])
        innovativeness_pred = innovativeness_model.predict([project_text])
        output_file.write("\nPrediction Objective: "+str(objective_pred))
        output_file.write("\nPrediction Actors: " + str(actor_pred))
        output_file.write("\nPrediction Outputs: " + str(outputs_pred))
        output_file.write("\nPrediction Innovativeness: "+str(innovativeness_pred))
        output_file.write("\n\nLinks: " +  str(common_regex_processed.links))
        output_file.write("\n\nEmails: " + str(common_regex_processed.emails))
        output_file.write("\n\nPhones: " + str(common_regex_processed.phones))
        project_text = project_text.decode('utf-8','ignore').strip()
        st = StanfordTagger('Resources')
        short_texts = project_text.splitlines()
        classified_text = []
        for t in short_texts:
            classified_text = classified_text + st.tag_text(t)
        st = None
        extracted_locations = []
        extracted_orgs = []
        for o in all_organisations:
            o = o.lower()
            if o.encode('utf-8','ignore').strip().lower() in project_text.encode('utf-8','ignore').strip().lower():
                extracted_orgs.append(o)
            # This performs lexicon matching with calculating Levenstein's distance, however because of the low performance it is not usable
            # if find_org(o, nltk.word_tokenize(project_text)) == True:
            #     extracted_orgs.append(o)
        print(classified_text)
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

        print "Organisations:"+str(extracted_orgs)
        print "-----------"
        print "Locations:"+str(extracted_locations)
        output_file.write("\nLocations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_locations)))
        output_file.write("\nOrganisations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_orgs)))


        output_file.write("\nOntology topics and keywords:")
        r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data=project_text.encode('ascii','ignore'))
        print(r.status_code, r.reason)
        print(r.text)
        if "Error" in r.text :
            continue
        data = json.loads(r.text)
        for clas in data["classification"]:
            print "Class:" + clas + ":" + str(data["classification"][clas]["score"])
            f_gate.write("\nTopic:"+clas+"  "+str(data["classification"][clas]["score"]))
            output_file.write("\nTopic:"+clas+"  "+str(data["classification"][clas]["score"]))
            print "Keywords"
            output_file.write("\nKeywords:")
            f_gate.write("\nKeywords:")
            for key in data["classification"][clas]["keywords"]:
                print key + ":" + str(data["classification"][clas]["keywords"][key])
                output_file.write("\n")
                output_file.write(key + "   " + str(data["classification"][clas]["keywords"][key]))
                f_gate.write("\n")
                f_gate.write(key + "   " + str(data["classification"][clas]["keywords"][key]))
        f_gate.close()
    output_file.close()