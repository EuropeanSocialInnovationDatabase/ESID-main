from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
from NER.StanfordNER import StanfordTagger
import requests
import json
from langdetect import detect
import os
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
    directory = "Sample4"
    text_too_short = 0
    not_english = 0
    files_made = 0
    no_website = 0
    no_desc = 0
    if not os.path.exists(directory):
        os.makedirs(directory)



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

    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects order by RAND() limit 500"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        #f_gate = open("Outputs/p_"+res[0]+".txt",'w')
        project_names.append(res[0])
        output_file.write("\n================================\n")
        output_file.write("Project name: "+res[0])
        #output_file.write("\nWebpage: "+res[1])
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        documents = mongo_db.projects_actors2.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(50)
        project_text = ""
        for doc in documents:
            project_text = project_text +  doc["page_title"]
            project_text = project_text + "\n===============================\n\n"
            project_text = project_text + doc["text"]

        if project_text == "" or project_text == " ":
            text_too_short = text_too_short + 1
            continue
        try:
            language = detect(project_text)
        except:
            text_too_short = text_too_short + 1
            continue
        print "Language:"+str(language)
        if language!="en":
            continue
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
        #f_gate.write(project_text)

        project_text = project_text.decode('utf-8','ignore').strip()
        if len(project_text)>500:


            f = open("Sample4/"+str(pro.idProject)+".txt","w")
            f.write(project_text)
            f.close()