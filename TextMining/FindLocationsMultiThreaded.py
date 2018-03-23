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
import threading
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

def doWork(pro):

    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    documents = mongo_db.translated.find({"mysql_databaseID": str(pro.idProject)}, no_cursor_timeout=True).batch_size(
        30)
    project_text = ""
    for doc in documents:
        project_text = project_text + doc['translation']

    common_regex_processed = CommonRegex(project_text)
    f_gate.write(project_text)

    project_text = project_text.decode('utf-8', 'ignore').strip()
    st = StanfordTagger('Resources')
    short_texts = project_text.splitlines()
    classified_text = []
    for t in short_texts:
        classified_text = classified_text + st.tag_text(t)
    st = None
    extracted_locations = []

    print(classified_text)
    loc_full_name = ""
    org_full_name = ""
    was_prev_loc = False
    was_prev_org = False
    for t in classified_text:
        if t[1] == "LOCATION":
            if was_prev_loc == False:
                loc_full_name = loc_full_name + " " + t[0]
                was_prev_loc = True
                continue
            if was_prev_loc == True:
                loc_full_name = loc_full_name + " " + t[0]
        if t[1] != "LOCATION":
            if was_prev_loc:
                extracted_locations.append(loc_full_name)
                loc_full_name = ""
            was_prev_loc = False
    freq_location = {}
    for location in extracted_locations:
        if location in freq_location:
            freq_location[location] = freq_location[location] + 1
        else:
            freq_location[location] = 1
    most_freq = ""
    freq = 0
    for loc in freq_location:
        if freq_location[loc] > freq:
            freq = freq_location[loc]
            most_freq = loc
    print "-----------"
    print "Locations:" + str(most_freq) + "   " + str(freq)
    with lock:
        output_file = open("output.txt", 'a')
        output_file.write("\n================================\n")
        output_file.write("Project name: " + pro.name)
        output_file.write("\nWebpage: " + pro.webpage)
        output_file.write("\nProject_id:" + str(pro.idProject))
        output_file.write("\nLocations:" + str(most_freq) + "   " + str(freq))
        output_file.write("\nLocations:")
        output_file.write("\n")
        output_file.write(str(set(extracted_locations)))
        output_file.write(str(set(freq_location)))
        output_file.close()
    pass

lock = threading.Lock()
if __name__ == '__main__':
    project_names = []
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects  limit 30,30"
    cursor.execute(sql_projects)
    results = cursor.fetchall()


    for res in results:

        f_gate = open("Outputs/p_"+res[0]+".txt",'w')
        project_names.append(res[0])

        pro = Project()
        pro.name = res[0]
        pro.webpage = res[1]
        pro.first_datasource = res[2]
        pro.first_datasource_id = res[3]
        pro.idProject = res[4]
        project_list.append(pro)

        processThread = threading.Thread(target=doWork, args=(pro,))  # <- note extra ','
        processThread.start()

