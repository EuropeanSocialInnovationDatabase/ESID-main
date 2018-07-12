#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
import csv
import MySQLdb
from TextMining.database_access import *
from TextMining.NER.StanfordNER import StanfordTagger
from pymongo import MongoClient

db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
db.set_character_set("utf8")
db2.set_character_set("utf8")
cursor = db.cursor()
nltk.internals.config_java(options='-Xmx3024m')
cursor2 = db2.cursor()
print("Selecting projects from mysql")
sql_projects = "Select idProjects,ProjectName,ProjectWebpage, City, Country, Longitude, Latitude from Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and Longitude is Null and Latitude is Null and (City is Null or City <> '') and idProjects>5462"
cursor.execute(sql_projects)
results = cursor.fetchall()
csvfile = open('locations5.csv', 'w')
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
for row in results:
    idProject = row[0]
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
    documents = mongo_db.translated_all.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(100)
    projectText = ""
    for doc in documents:
        projectText = projectText+" "+doc['translation']
    documents2 = mongo_db.translated_all_wayback2.find({"mysql_databaseID": str(idProject)}, no_cursor_timeout=True).batch_size(
        100)
    for doc in documents2:
        projectText = projectText+" "+doc['translation']
    # projectText contains all the text, both from archive, description and crawled normally
    cities = {}
    countries = {}
    try:
        st_tagger = StanfordTagger('../Resources')
        tags = st_tagger.tag_text(projectText)
        #print tags
        for tag in tags:
            if tag[1]=='LOCATION':# Check whether city
                new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0".format(
                    tag[0].encode('utf-8'))
                # print new_sql
                try:
                    cursor2.execute(new_sql)
                    results2 = cursor2.fetchall()
                    FoundCity = ""
                    FoundCountry = ""
                    found = False
                    for r in results2:
                        FoundCity = r[0]
                        FoundCountry = r[1]
                        if FoundCity not in cities.keys():
                            cities[str(FoundCity)] = 1
                        else:
                            cities[str(FoundCity)] = cities[str(FoundCity)] + 1
                        if FoundCountry not in countries.keys():
                            countries[str(FoundCountry)] = 1
                        else:
                            countries[str(FoundCountry)] = countries[str(FoundCountry)] + 1
                    new_sql = "SELECT CountryName FROM Semanticon.Country where CountryName like '{0}'".format(
                        tag[0].encode('utf-8'))
                    # print new_sql
                    cursor2.execute(new_sql)
                    results2 = cursor2.fetchall()
                    for r in results2:
                        FoundCountry = r[0]
                        if FoundCountry not in countries.keys():
                            countries[str(FoundCountry)] = 1
                        else:
                            countries[str(FoundCountry)] = countries[str(FoundCountry)] + 1
                except:
                    print("Cannot handle string: "+tag[0])
    except:
        print("Tagger cannot handle this project")
    print cities
    print countries
    max_city = ""
    max_city_count = 0
    max_country = ""
    max_country_count = 0
    for city in cities:
        new_sql = "SELECT CountryName FROM Semanticon.Country where CountryName like '{0}'".format(
            city.encode('utf-8'))
        # print new_sql
        cursor2.execute(new_sql)
        results2 = cursor2.fetchall()
        if len(results2)>0:
            continue
        if city == "uk":
            continue
        if city == "republic":
            continue
        if cities[city]>max_city_count:
            max_city_count = cities[city]
            max_city = city
    for country in countries:
        if countries[country]>max_country_count:
            max_country_count = countries[country]
            max_country = country
    print "Max city:"+max_city
    print "Max country:"+max_country
    if projectWebpage == None:
        projectWebpage = ""
    if projectName == None:
        projectName = ""
    writer.writerow([idProject,projectName.encode('utf-8'),projectWebpage.encode('utf-8'),max_city.encode('utf-8'),max_country.encode('utf-8')])
