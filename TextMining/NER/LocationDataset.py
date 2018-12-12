#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
import csv
import MySQLdb
from TextMining.database_access import *
from TextMining.NER.StanfordNER import StanfordTagger
from nltk.tokenize import sent_tokenize
from pymongo import MongoClient

db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
db.set_character_set("utf8")
db2.set_character_set("utf8")
cursor = db.cursor()
nltk.internals.config_java(options='-Xmx3024m')
cursor2 = db2.cursor()
print("Selecting projects from mysql")
sql_projects = "Select idProjects,ProjectName,ProjectWebpage, City, Country, Longitude, Latitude from Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and idProjects>2100 and Country<>''"
cursor.execute(sql_projects)
results = cursor.fetchall()
csvfile = open('locations_dataset2.csv', 'w')
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

for row in results:
    idProject = row[0]
    print(idProject)
    projectName = row[1]
    projectWebpage = row[2]
    projectCity = row[3]
    ProjectCountry = row[4]
    if ProjectCountry == "UK":
        ProjectCountry = "United Kingdom"
    if ProjectCountry == "USA":
        ProjectCountry = "United States"
    if ProjectCountry == "Russian Federation":
        ProjectCountry = "Russia"
    if ProjectCountry == "Polonia":
        ProjectCountry = "Poland"
    if projectCity == "Prishtina":
        projectCity = "Pristina"
    documents = mongo_db.crawl20180801_translated.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(100)
    projectText = ""
    for doc in documents:
        projectText = projectText+" \n"+doc['translation']
    documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(
        100)
    for doc in documents2:
        projectText = projectText+" \n"+doc['translation']
    # projectText contains all the text, both from archive, description and crawled normally
    sql2 = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects={0}".format(idProject)
    try:
        cursor.execute(sql2)
    except:
        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        cursor = db.cursor()
        cursor.execute(sql2)
    results2 = cursor.fetchall()
    for res in results2:
        description = res[2]
        projectText = projectText + " \n" +description
    cities = {}
    countries = {}
    try:
        st_tagger = StanfordTagger('../Resources')
        sentences = sent_tokenize(projectText)
        for sent in sentences:
            tags = st_tagger.tag_text(sent)
            for tag in tags:
                if tag[1] == 'LOCATION' and (tag[0].encode('utf-8')==projectCity or tag[0].encode('utf-8')==ProjectCountry):
                    writer.writerow([idProject,sent.encode('utf-8'),tag[0].encode('utf-8'),'pos'])
                elif tag[1] == 'LOCATION' and (tag[0].encode('utf-8')!=projectCity and tag[0].encode('utf-8')!=ProjectCountry):
                    writer.writerow([idProject,sent.encode('utf-8'), tag[0].encode('utf-8'), 'neg'])
    except:
        print("There is error!")
