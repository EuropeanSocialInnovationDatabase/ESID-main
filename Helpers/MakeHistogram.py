#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from pymongo import MongoClient
import nltk
import MySQLdb
import time
from database_access import *
from langdetect import detect
from mtranslate import translate
from nltk.metrics.distance import edit_distance
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
    csv_file = open("histogram2.csv","wb")
    csv_writer = csv.writer(csv_file, delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
    print("Initializing")
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    print("Selecting projects from mysql")
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where Exclude=0"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    print("Initializing Mongo")
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    translationTimeout = 0

    for res in results:
        #project_names.append(res[0])
        print("Reading project "+str(res[0]) )
        number_of_pages = 0
        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)
        print("Grabbing documents from Mongo")
        documents = mongo_db.all_with_rule.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(200)
        project_text = ""
        original_text = ""
        # if documents.count()>1000:
        #     print("Too many documents")
        #     documents = mongo_db.all_with_rule.find({"mysql_databaseID": str(pro.idProject),"page_title":{"$regex":"about"}},
        #                                                no_cursor_timeout=True).batch_size(100)
        print("Making a big document")

        for doc in documents:
            number_of_pages = number_of_pages + 1  
            #project_text = project_text +  doc["page_title"]
            #project_text = project_text + "\n===============================\n\n"
            project_text = project_text + doc["text"]


        project_text = project_text.encode('utf-8',errors='ignore').strip()
        print("Grabbing descriptions")
        sql_desc = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(pro.idProject)
        cursor.execute(sql_desc)
        f_desc = cursor.fetchall()
        print("Appending descriptions")
        description_len = 0
        description_pages = 0
        for d in f_desc:
            project_text = project_text+ " \n\n "+d[2].encode('utf-8',errors='ignore').strip()
            original_text = original_text+ " \n\n "+d[2].encode('utf-8',errors='ignore').strip()
            description_pages = description_pages + 1
            description_len = description_len + len(d[2].encode('utf-8',errors='ignore').strip())
        tokens = nltk.word_tokenize(project_text.decode("utf-8",errors='ignore'))
        csv_writer.writerow([pro.name,str(len(tokens))])
    csv_file.close()



    print "Translation timeouts on: "+str(translationTimeout)+" pages"

