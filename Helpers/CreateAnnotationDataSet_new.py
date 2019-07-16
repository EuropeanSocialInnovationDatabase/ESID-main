from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
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
    #output_file = open("output.txt",'w')
    directory = "Sample100_ann"
    text_too_short = 0
    not_english = 0
    files_made = 0
    no_website = 0
    no_desc = 0
    if not os.path.exists(directory):
        os.makedirs(directory)


    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()

    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects left join TypeOfSocialInnotation on idProjects = Projects_idProjects where Exclude=0 and idProjects>4000 and idProjects<14000 and Social_Innovation_overall is not null and SourceModel like '%Manual%'"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID

    for res in results:
        #f_gate = open("Outputs/p_"+res[0]+".txt",'w')
        #project_names.append(res[0])
        #output_file.write("\n================================\n")
        #output_file.write("Project name: "+res[0])
        #output_file.write("\nWebpage: "+res[1])
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        documents = mongo_db.translated_all.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(50)
        project_text = ""
        for doc in documents:
            project_text = project_text + doc["translation"]

        if project_text == "" or project_text == " ":
            text_too_short = text_too_short + 1
            continue


        project_text = project_text.encode('utf-8').strip()
        sql_desc = "SELECT * FROM EDSI.AdditionalProjectData where (FieldName like '%Description%' or FieldName like '%Challenges Addressed%' " \
                  "or FieldName like '%Actor%' or FieldName like '%Impact%' or FieldName like '%Social%' or FieldName like '%Note%' or FieldName like '%Purpose%') and Projects_idProjects=" + str(pro.idProject)
        cursor.execute(sql_desc)
        f_desc = cursor.fetchall()
        for d in f_desc:
            project_text = project_text+ " \n\n "+d[2].encode('utf-8').strip()
        #f_gate.write(project_text)

        project_text = project_text.decode('utf-8','ignore').strip()
        if len(project_text)>500 and len(project_text)<300000:
            print("Writing "+str(pro.idProject))
            f = open("Sample100_ann/"+str(pro.idProject)+".txt","w")
            f.write(project_text)
            f.write("\r\n WHOLE PROJECT MARK")
            f.close()
            f = open('Sample10_ann/' + str(pro.idProject) + ".ann", 'w')
            f.close()