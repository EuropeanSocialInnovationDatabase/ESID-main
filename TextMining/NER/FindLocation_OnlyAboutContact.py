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
# sql_projects = "Select idProjects,ProjectName,ProjectWebpage from Projects where Exclude = 0"
# cursor.execute(sql_projects)
# results = cursor.fetchall()
csvfile = open('locations_tab_new_contacts_abouts.csv', 'w')
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
documents = mongo_db.crawl20190109.find({"page_title":{"$regex":"([a|A]bout)|([C|c]ontact)"}}, no_cursor_timeout=True).batch_size(100)
for doc in documents:
    text = doc['text']
    project_id = doc['mysql_databaseID']
    url = doc['url']
    projectName = doc['name']
    projectWebpage = url
    cities = {}
    countries = {}
    try:
        st_tagger = StanfordTagger('../Resources')
        tags = st_tagger.tag_text(text)
        #print tags
        for tag in tags:
            if tag[1]=='LOCATION':# Check whether city
                new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0 order by Population desc".format(
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
    cursor.execute("Select City,Country from ProjectLocation where Projects_idProjects=" + str(project_id))
    results2 = cursor.fetchall()
    database_city = ""
    database_country = ""
    for r in results2:
        database_city = r[0]
        if database_city!= None:
            database_city = database_city.encode('utf-8')
        database_country = r[1]
        if database_country!= None:
            database_country = database_country.encode('utf-8')
    writer.writerow([project_id, projectName.encode('utf-8'), projectWebpage.encode('utf-8'), max_city.encode('utf-8'),
                     max_country.encode('utf-8'), database_city, database_country])

    #writer.writerow([idProject,projectName.encode('utf-8'),projectWebpage.encode('utf-8'),max_city.encode('utf-8'),max_country.encode('utf-8')])
