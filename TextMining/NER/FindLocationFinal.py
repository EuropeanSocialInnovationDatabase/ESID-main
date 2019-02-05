#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
import csv
import MySQLdb
from TextMining.database_access import *
from TextMining.NER.StanfordNER import StanfordTagger
from pymongo import MongoClient
from langdetect import detect
from mtranslate import translate
translationTimeout = 0
def checkEngAndTranslate(project_text):
    global translationTimeout
    print("Language detection")
    language = 'en'
    if project_text == "":
        language = 'en'
    else:
        try:
            language = detect(project_text)
        except:
            print("Error translating")
    original_text = project_text
    print "Language:" + str(language)
    if language == "en":
        return project_text
    if language != "en":
        print("Start translating")
        tokens = nltk.word_tokenize(project_text)
        i = 0
        text_to_translate = ""
        translated = ""
        while i < len(tokens):
            for j in range(0, 200):
                if i >= len(tokens):
                    continue
                text_to_translate = text_to_translate + " " + tokens[i]
                i = i + 1
            try:
                en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
            except:
                print "Timeout translation"
                translationTimeout = translationTimeout + 1
            translated = translated + " " + en_text
            text_to_translate = ""
        print translated
        project_text = translated
        print("End translating")
        return project_text
    return project_text

def FindLocation(project_text,st_tagger,countries1):
    try:
        cities = {}
        countries = {}
        countries_boosted = {}
        tags = st_tagger.tag_text(project_text)
        # print tags
        list = ["uk", "republic", "union", "norway","china"] + countries1
        for tag in tags:
            if tag[1] == 'LOCATION':  # Check whether city
                new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0 order by Population desc".format(
                    tag[0].encode('utf-8'))
                try:
                    cursor2.execute(new_sql)
                    results2 = cursor2.fetchall()
                    FoundCity = ""
                    FoundCountry = ""
                    found = False
                    for r in results2:
                        FoundCity = r[0]
                        FoundCountry = r[1]
                        if tag[0].lower() in list:
                            continue

                        if FoundCity not in cities.keys():
                            cities[str(FoundCity)] = 1
                        else:
                            cities[str(FoundCity)] = cities[str(FoundCity)] + 1
                        if FoundCountry not in countries_boosted.keys():
                            countries_boosted[str(FoundCountry)] = 1
                        else:
                            countries_boosted[str(FoundCountry)] = countries_boosted[str(FoundCountry)] + 1
                        break
                    new_sql = "SELECT CountryName FROM Semanticon.Country where CountryName like '{0}'".format(
                        tag[0].encode('utf-8'))
                    cursor2.execute(new_sql)
                    results2 = cursor2.fetchall()
                    for r in results2:
                        FoundCountry = str(r[0])
                        if FoundCountry not in countries.keys():
                            countries[str(FoundCountry)] = 1
                            if FoundCountry not in countries_boosted.keys():
                                countries_boosted[str(FoundCountry)] = 1
                            else:
                                countries_boosted[str(FoundCountry)] = countries_boosted[str(FoundCountry)] + 1
                        else:
                            countries[str(FoundCountry)] = countries[str(FoundCountry)] + 1
                            countries_boosted[str(FoundCountry)] = countries_boosted[str(FoundCountry)] + 1
                except:
                    print("Cannot handle string: " + tag[0])
    except:
        print("Error with st_tagger")
        st_tagger = StanfordTagger('../Resources')

    print cities
    print countries
    print countries_boosted
    max_city = ""
    max_city_count = 0
    max_country = ""
    max_country_count = 0
    max_country_boosted_count = 0
    max_country_boosted = ""
    for city in cities:
        if cities[city] > max_city_count:
            max_city_count = cities[city]
            max_city = city
    for country in countries:
        if countries[country] > max_country_count:
            max_country_count = countries[country]
            max_country = country
    for country in countries_boosted:
        if countries_boosted[country] > max_country_boosted_count:
            max_country_boosted_count = countries_boosted[country]
            max_country_boosted = country
    print "Max city:" + max_city
    print "Max country:" + max_country
    print "Max country boosted:" + max_country
    return max_city,max_country,max_country_boosted,st_tagger

def findBestMatch(FoundCity,FoundCountry):
    for i in range(0,3):
        for j in range(0,3):
            if len(FoundCity)>i and len(FoundCountry)>j:
                sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Country_CountryName like '{1}' and Population>0 order by Population desc".format(FoundCity[i]['City'].encode('utf-8'),FoundCountry[j]['Country'].encode('utf-8'))
                cursor.execute(sql)
                resul = cursor.fetchall()
                if len(resul)>0:
                    return FoundCity[i]['City'],FoundCountry[j]['Country'],FoundCity[i]['Confidence']
    return "","",0




csvfile = open('locations_final2.csv', 'w')
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(["ProjectID","ProjectName","FoundCity","FoundCountry","DatabaseCity","DatabaseCountry","Confidence","FoundWhere","Website"])
db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
db.set_character_set("utf8")
db2.set_character_set("utf8")
cursor = db.cursor()
nltk.internals.config_java(options='-Xmx3024m')
country_sql = "SELECT CountryName FROM Semanticon.Country"
cursor.execute(country_sql)
results2 = cursor.fetchall()
countries = []
for r in results2:
    countries.append(r[0].lower())
cursor2 = db2.cursor()
print("Selecting projects from mysql")
sql_projects = "Select idProjects,ProjectName,ProjectWebpage from Projects where Exclude = 0 and idProjects>=2000"
cursor.execute(sql_projects)
results = cursor.fetchall()
csvfile = open('locations_tab2.csv', 'w')
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
st_tagger = StanfordTagger('../Resources')
for row in results:
    idProject = row[0]
    projectName = row[1]
    projectWebpage = row[2]
    page_at = ""
    FoundCountry = []
    FoundCity = []
    cursor.execute("Select City,Country from ProjectLocation where Projects_idProjects=" + str(idProject))
    results3 = cursor.fetchall()
    database_city = ""
    database_country = ""
    for r in results3:
        database_city = r[0]
        if database_city != None:
            database_city = database_city.encode('utf-8')
        database_country = r[1]
        if database_country != None:
            database_country = database_country.encode('utf-8')

    documents = mongo_db.crawl20190109.find(
        {"mysql_databaseID": str(idProject), "page_title": {"$regex": "([C|c]ontact)"}},
        no_cursor_timeout=True).batch_size(100)
    page_at = "Contact"
    projectText = ""
    for doc in documents:
        text = doc['text']
        projectText = projectText + " " + text
    projectText = checkEngAndTranslate(projectText)
    city, country, country_boosted,st_tagger = FindLocation(projectText, st_tagger,countries)
    print city
    print country
    print country_boosted
    print page_at
    if city!="" and city!="uk":
        FoundCity.append({"City":city,"Page":"Contact","Confidence":10})
    if country!="":
        FoundCountry.append({"Country":country,"Page":"Contact","Confidence":10})
    if len(FoundCity)>0 and len(FoundCountry)>0:
        try:
            writer.writerow([idProject,projectName,FoundCity[0]["City"].title(),FoundCountry[0]["Country"],database_city,database_country,FoundCity[0]["Confidence"],"Contact",projectWebpage])
        except:
            print("Problem")
        continue

    documents = mongo_db.crawl20190109.find({"mysql_databaseID": str(idProject),"page_title":{"$regex":"([a|A]bout)"}}, no_cursor_timeout=True).batch_size(100)
    page_at = "About"
    projectText = ""
    for doc in documents:
        text = doc['text']
        projectText = projectText + " " + text
    projectText = checkEngAndTranslate(projectText)
    city, country, country_boosted,st_tagger = FindLocation(projectText,st_tagger,countries)
    print city
    print country
    print country_boosted
    print page_at
    CityAlreadyFound = False
    CountryAlreadyFound = False
    if city!="":
        for fc in FoundCity:
            if city.lower().replace(" ","") == fc["City"].lower().replace(" ",""):
                fc["Confidence"] = fc["Confidence"] + 8
                CityAlreadyFound = True
        if CityAlreadyFound == False:
            FoundCity.append({"City": city, "Page": "About", "Confidence": 8})
    if country_boosted!="":
        for fc in FoundCountry:
            if country_boosted.lower().replace(" ","") == fc["Country"].lower().replace(" ",""):
                fc["Confidence"] = fc["Confidence"] + 8
                CountryAlreadyFound = True
        if CountryAlreadyFound == False:
            FoundCountry.append({"Country": country_boosted, "Page": "About", "Confidence": 8})
    c,cn,conf = findBestMatch(FoundCity,FoundCountry)
    if c!="" and cn!="":
        try:
            writer.writerow(
            [idProject, projectName, c.title(), cn, database_city, database_country,
             conf, "About",projectWebpage,])
        except:
            print("Problem!")
        continue

    desc_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%desc%' and Projects_idProjects="+str(idProject);
    cursor.execute(desc_sql)
    results2 = cursor.fetchall()
    projectText = ""
    page_at = "Description"
    for r2 in results2:
        text = r2[2]
        projectText = projectText + " " + text
    projectText = checkEngAndTranslate(projectText)
    city, country, country_boosted,st_tagger = FindLocation(projectText, st_tagger,countries)
    print city
    print country
    print country_boosted
    print page_at

    CityAlreadyFound = False
    CountryAlreadyFound = False
    if city!="" and city!="uk":
        for fc in FoundCity:
            if city.lower().replace(" ","") == fc["City"].lower().replace(" ",""):
                fc["Confidence"] = fc["Confidence"] + 6
                CityAlreadyFound = True
        if CityAlreadyFound == False:
            FoundCity.append({"City": city, "Page": "Description", "Confidence": 6})
    if country_boosted!="":
        for fc in FoundCountry:
            if country_boosted.lower().replace(" ","") == fc["Country"].lower().replace(" ",""):
                fc["Confidence"] = fc["Confidence"] + 6
                CountryAlreadyFound = True
        if CountryAlreadyFound == False:
            FoundCountry.append({"Country": country_boosted, "Page": "Description", "Confidence": 6})
    c,cn,conf = findBestMatch(FoundCity,FoundCountry)
    if c!="" and cn!="":
        print(c)
        print(cn)
        print(database_city)

        writer.writerow(
        [idProject, projectName, c.title().encode('utf-8'), cn.encode('utf-8'), database_city, database_country.encode('utf-8'),
         conf, "Description",projectWebpage.encode('utf-8')])

        continue

    documents = mongo_db.crawl20190109.find(
        {"mysql_databaseID": str(idProject)},
        no_cursor_timeout=True).batch_size(100)
    projectText = ""
    if documents.count()<=2:
        page_at = "One page"
        for doc in documents:
            text = doc['text']
            projectText = projectText + " " + text
        projectText = checkEngAndTranslate(projectText)
        city, country, country_boosted,st_tagger = FindLocation(projectText, st_tagger,countries)
        print city
        print country
        print country_boosted
        print page_at

        CityAlreadyFound = False
        CountryAlreadyFound = False
        if city != "" and city!="uk":
            for fc in FoundCity:
                if city.lower().replace(" ", "") == fc["City"].lower().replace(" ", ""):
                    fc["Confidence"] = fc["Confidence"] + 4
                    CityAlreadyFound = True
            if CityAlreadyFound == False:
                FoundCity.append({"City": city, "Page": "One page", "Confidence": 4})
        if country_boosted != "":
            for fc in FoundCountry:
                if country_boosted.lower().replace(" ", "") == fc["Country"].lower().replace(" ", ""):
                    fc["Confidence"] = fc["Confidence"] + 4
                    CountryAlreadyFound = True
            if CountryAlreadyFound == False:
                FoundCountry.append({"Country": country_boosted, "Page": "One page", "Confidence": 4})
        c, cn, conf = findBestMatch(FoundCity, FoundCountry)
        if c != "" and cn != "":
            try:
                writer.writerow(
                [idProject, projectName, c.title(), cn, database_city, database_country,
                 conf, "One page", projectWebpage, ])
            except:
                print("Problem!!!")
            continue
    else:
        main_text = ""
        for doc in documents:
            if doc['url'].replace(" ","").lower() == projectWebpage.replace(" ","").lower():
                main_text = doc['text']
                page_at = "Main page"
            if main_text !="":
                break
        projectText = main_text
        if projectText !="":
            projectText = checkEngAndTranslate(projectText)
            city, country, country_boosted,st_tagger = FindLocation(projectText, st_tagger,countries)
            print city
            print country
            print country_boosted
            print page_at
            CityAlreadyFound = False
            CountryAlreadyFound = False
            if city != "" and city!="uk":
                for fc in FoundCity:
                    if city.lower().replace(" ", "") == fc["City"].lower().replace(" ", ""):
                        fc["Confidence"] = fc["Confidence"] + 2
                        CityAlreadyFound = True
                if CityAlreadyFound == False:
                    FoundCity.append({"City": city, "Page": "Main page", "Confidence": 2})
            if country_boosted != "":
                for fc in FoundCountry:
                    if country_boosted.lower().replace(" ", "") == fc["Country"].lower().replace(" ", ""):
                        fc["Confidence"] = fc["Confidence"] + 2
                        CountryAlreadyFound = True
                if CountryAlreadyFound == False:
                    FoundCountry.append({"Country": country_boosted, "Page": "Main page", "Confidence": 2})
            c, cn, conf = findBestMatch(FoundCity, FoundCountry)
            if c != "" and cn != "":
                try:
                    writer.writerow(
                    [idProject, projectName, c.title(), cn, database_city, database_country,
                     conf, "Main page", projectWebpage, ])
                except:
                    print("A bit of a problem")
                continue
    projectText = ""
    for doc in documents:
        projectText = projectText + " "+doc["text"]
    page_at = "General"
    projectText = checkEngAndTranslate(projectText)
    city, country, country_boosted,st_tagger = FindLocation(projectText, st_tagger,countries)
    print city
    print country
    print country_boosted
    print page_at

    CityAlreadyFound = False
    CountryAlreadyFound = False
    if city != "" and city!="uk":
        for fc in FoundCity:
            if city.lower().replace(" ", "") == fc["City"].lower().replace(" ", ""):
                fc["Confidence"] = fc["Confidence"] + 1
                CityAlreadyFound = True
        if CityAlreadyFound == False:
            FoundCity.append({"City": city, "Page": "General", "Confidence": 1})
    if country_boosted != "":
        for fc in FoundCountry:
            if country.lower().replace(" ", "") == fc["Country"].lower().replace(" ", ""):
                fc["Confidence"] = fc["Confidence"] + 1
                CountryAlreadyFound = True
        if CountryAlreadyFound == False:
            FoundCountry.append({"Country": country_boosted, "Page": "General", "Confidence": 1})
    c, cn, conf = findBestMatch(FoundCity, FoundCountry)
    if c != "" and cn != "":
        try:
            writer.writerow(
            [idProject, projectName, c.title(), cn, database_city, database_country,
             conf, "General", projectWebpage, ])
        except:
            print("A bit of a problem")
        continue
    if len(FoundCity)>0:
        c = FoundCity[0]["City"]
    if len(FoundCountry)>0:
        cn = FoundCountry[0]["Country"]
    try:
        if c!="" or cn!="":
            writer.writerow(
            [idProject, projectName, c.title(), cn, database_city, database_country,
            0.5, "AfterAll", projectWebpage, ])
    except:
        print("Sort of a problem")
csvfile.close()