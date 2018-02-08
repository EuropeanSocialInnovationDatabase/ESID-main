#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from TextMining.NER.StanfordNER import StanfordTagger
import requests
import json
from database_access import *
from langdetect import detect
from mtranslate import translate
import csv
from nltk.metrics.distance import edit_distance
import pickle
from commonregex import CommonRegex

class Organisation:
    def __init__(self):
        self.organisation_id = ""
        self.database_id = -1
        self.organisation_name = "" # ActorName
        self.website = "" #ActorWebsite
        self.short_description = "" # ActorsAdditionalData-ActorShortDescription
        self.long_description = ""# ActorsAdditionalData-ActorLongDescription
        self.country ="" # Location.Country
        self.region = "" #Location.City
        self.latitude = -1 #Location.Latitude
        self.longitude = -1#Location.Longitude
        self.address = ""#Location.address
        self.organisation_type = ""#Actor.Type
        self.organisation_size= ""#Size
        self.start_date = ""#StartDate
        self.linked_project_ids = [] # Actors_has_projects
        self.tags = [] # ActorsAdditionalData
        self.network_tags = [] #ActorsAdditionalData
        self.facebook = None # ActorFacebookPage


class Project:
    def __init__(self):
        self.project_id = ""
        self.database_id = -1
        self.project_name = "" # ProjectName
        self.website = "" # ProjectWebpage
        self.short_description = "" # AdditionalProjectData
        self.long_description = "" # AdditionalProjectData
        self.social_impact = "" #OutreachImpact
        self.start_date = "" #DateStart
        self.end_date = "" #DateEnd
        self.country = "" # ProjectLocation
        self.region = "" # City
        self.latitude = -1 #Longitude
        self.longitude = -1 # Latitude
        self.linked_organisation_ids = [] #Actor_has_Projects
        self.who_we_help_tags = [] #AdditionalProjectData.WhoWeHelp
        self.support_tags = [] # AdditionalProjectData.SupportTags
        self.focus = [] # AdditionalProjectData.Focus
        self.technology = [] # AdditionalProjectData.Technology
        self.facebook = None

class Project_ne:
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
    objectives_model = pickle.load(open('../Classifiers/Models/naive_bayes_objectives.sav', 'rb'))
    actors_model = pickle.load(open('../Classifiers/Models/naive_bayes_actors.sav', 'rb'))
    outputs_model = pickle.load(open('../Classifiers/Models/naive_bayes_outputs.sav', 'rb'))
    innovativeness_model = pickle.load(open('../Classifiers/Models/naive_bayes_innovativeness.sav', 'rb'))

    organisations_arg = "../../ESIDcrawlers/DownloadedDatabaseTransformers/organisations.csv"
    projects_arg = "../../ESIDcrawlers/DownloadedDatabaseTransformers/projects.csv"
    organisations = []
    with open(organisations_arg, 'rb') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in orgreader:
            if(i==0):
                i+=1
                continue
            org = Organisation()
            org.organisation_id = row[0]
            org.organisation_name = row[1]
            org.website = row[2]
            org.short_description = row[3]
            org.long_description = row[4]
            org.country = row[5]
            org.region = row[6]
            org.latitude=row[7]
            org.longitude = row[8]
            org.address = row[9]
            org.organisation_type = row[10]
            org.organisation_size = row[11]
            org.start_date = row[12]
            org.linked_project_ids = row[13].replace('"','').split(',')
            org.tags = row[14].replace('"','').split(',')
            org.network_tags = row[15].replace('"','').split(',')
            organisations.append(org)
            i+=1
    projects = []
    with open(projects_arg, 'rb') as csvfile:
        proreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in proreader:
            if (i == 0):
                i += 1
                continue
            pro = Project()
            pro.project_id = row[0]
            pro.project_name = row[1]
            pro.website = row[2]
            pro.short_description = row[3]
            pro.long_description = row[4]
            pro.social_impact = row[5]
            pro.start_date = row[6]
            pro.end_date = row[7]
            pro.country = row[8]
            pro.region = row[9]
            pro.latitude = row[10]
            pro.longitude = row[11]
            pro.linked_organisation_ids = row[12].replace('"','').split(',')
            pro.who_we_help_tags = row[13].replace('"','').split(',')
            pro.support_tags = row[14].replace('"','').split(',')
            pro.focus = row[15].replace('"','').split(',')
            pro.technology = row[16].replace('"','').split(',')
            projects.append(pro)
            i += 1

    project_names = []
    actor_names = []
    orglist_names = []
    with open('../Resources/orgreg_hei_export_.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        a = 0
        for row in spamreader:
            if a<2:
                a = a+1
                continue
            orglist_names.append(row[3])
            orglist_names.append(row[4])
            orglist_names.append(row[6])
            a = a+1
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_actors = "Select ActorName from Actors"
    cursor.execute(sql_actors)
    results = cursor.fetchall()
    for res in results:
        actor_names.append(res[0])
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where DataSources_idDataSources=1 limit 50"
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
        project_db = None
        for pro in projects:
            if pro.project_name == res[0]:
                project_db = pro
        real_org_names = []
        for id in project_db.linked_organisation_ids:
            for org in organisations:
                if id == org.organisation_id:
                    real_org_names.append(org.organisation_name)

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
        output_file.write("\n\nLinks: " + str(common_regex_processed.links))
        output_file.write("\n\nEmails: " + str(common_regex_processed.emails))
        output_file.write("\n\nPhones: " + str(common_regex_processed.phones))
        project_text = project_text.decode('utf-8','ignore').strip()
        st = StanfordTagger('../Resources')
        short_texts = project_text.splitlines()
        classified_text = []
        for t in short_texts:
            classified_text = classified_text + st.tag_text(t)
        st = None
        extracted_locations = []
        extracted_orgs = []
        for o in orglist_names:
            if o.lower() in project_text.encode('utf-8','ignore').strip().lower():
                extracted_orgs.append(o)
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

        print extracted_orgs
        print "-----------"
        print extracted_locations
        output_file.write("\nLocations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_locations)))
        output_file.write("\nOrganisations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_orgs)))
        output_file.write("\nReal Organisations:")
        output_file.write("\n")
        output_file.write(str(set(real_org_names)))
        f_gate.close()
    output_file.close()