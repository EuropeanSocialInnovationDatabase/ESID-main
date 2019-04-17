#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
import os
directory = "Dataset_SI_DB_Classification"
if not os.path.exists(directory):
    os.makedirs(directory)

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
sql = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%Manual%';"
cursor.execute(sql)
results = cursor.fetchall()

for res in results:
    Outputs = res[1]
    Objectives = res[2]
    Actors = res[3]
    Innovativeness = res[4]
    ProjectID = res[5]
    SI = res[6]
    if SI==None:
        SI = -1
    project_text = ""
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(ProjectID)},
                                                no_cursor_timeout=True).batch_size(100)
    for doc in documents:
        project_text = doc['translation'].encode('utf-8').strip()
    f = open(directory +"/"+ "p_" + str(ProjectID)+ "_"+str(Objectives)+"_"+str(Actors)+"_"+str(Outputs)+"_"+str(Innovativeness)+"_"+str(SI) + ".txt", "w")
    f.write(project_text)
    f.close()

documents = mongo_db.crawl20180801_excluded_translated.find().batch_size(100)
for doc in documents:
    project_text = doc['translation'].encode('utf-8','ignore').strip()
    f = open(directory + "/" + "p_" + str(
        doc['mysql_databaseID']) + "_" + "0" + "_" + "0" + "_" + "0" + "_" + "0" + "_" + "_" + "0" + ".txt",
             "w")
    f.write(project_text)
    f.close()