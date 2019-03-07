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
    language = 'en'
    if project_text == "":
        language = 'en'
    else:
        try:
            language = detect(project_text)
        except:
            print("Error translating")
    original_text = project_text
    print("Language:" + str(language))
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
                print("Timeout translation")
                translationTimeout = translationTimeout + 1
                en_text  = ""
            translated = translated + " " + en_text
            text_to_translate = ""
        print(translated)
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

    print(cities)
    print(countries)
    print(countries_boosted)
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
    print("Max city:" + max_city)
    print("Max country:" + max_country)
    print("Max country boosted:" + max_country)
    return max_city,max_country,max_country_boosted,st_tagger,cities,countries_boosted

def findBestMatch(FoundCity,FoundCountry,database_country):
    pair_candidates = []
    for i in range(0,5):
        for j in range(0,5):
            if len(FoundCity)>i and len(FoundCountry)>j:
                sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Country_CountryName like '{1}' and Population>0 order by Population desc".format(FoundCity[i]['City'].encode('utf-8'),FoundCountry[j]['Country'].encode('utf-8'))
                try:
                    cursor.execute(sql)
                except:
                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    db.set_character_set("utf8")
                    cursor = db.cursor()
                    cursor.execute(sql)
                resul = cursor.fetchall()
                if len(resul)>0:
                    pair_candidates.append({"City":FoundCity[i]['City'],"Country":FoundCountry[j]['Country'],"Score":(FoundCity[i]["Confidence"]+FoundCountry[j]["Confidence"]+0.5*(FoundCity[i]["Mentions"]+FoundCountry[j]["Mentions"]))})
                    #return FoundCity[i]['City'],FoundCountry[j]['Country'],FoundCity[i]['Confidence']
    City = ""
    Country = ""
    Score = 0
    selected_pair = None
    for pair in pair_candidates:
        if pair["Score"]>Score:
            Score = pair["Score"]
            City = pair["City"]
            Country = pair["Country"]
            selected_pair = pair
    if Country == "":
        return City, Country, Score
    elif database_country == "":
        return City,Country,Score
    elif Country in database_country:
        return City,Country,Score
    elif "Europe" in database_country or "international" in database_country or "amp" in database_country:
        return City, Country, Score
    else:
        while database_country != Country:
            if len(pair_candidates)>0:
                pair_candidates.remove(selected_pair)
                City = ""
                Country = ""
                Score = 0
                selected_pair = None
                for pair in pair_candidates:
                    if pair["Score"] > Score:
                        Score = pair["Score"]
                        City = pair["City"]
                        Country = pair["Country"]
                        selected_pair = pair
                if Country in database_country  :
                    return City, Country, Score
                if len(pair_candidates)==1:
                    return "",database_country,-1
            else:
                return City,Country,Score

def AddRelevantLocationsToList(city,country_boosted,FoundCity,FoundCountry,Confidence,PageName):
    CityAlreadyFound = False
    CountryAlreadyFound = False
    if city != "":
        for fc in FoundCity:
            if city.lower().replace(" ", "") == fc["City"].lower().replace(" ", ""):
                fc["Confidence"] = fc["Confidence"] + Confidence
                if country_boosted in ct.keys():
                    fc["Mentions"] = fc["Mentions"] + ct[country_boosted]
                CityAlreadyFound = True
        if CityAlreadyFound == False:
            FoundCity.append({"City": city, "Page": PageName, "Confidence": Confidence,"Mentions":ct[city]})
            for c in ct:
                if city == c:
                    continue
                FoundCity.append({"City": c, "Page": PageName, "Confidence": Confidence,"Mentions":ct[c]})
    if country_boosted != "":
        for fc in FoundCountry:
            if country_boosted.lower().replace(" ", "") == fc["Country"].lower().replace(" ", ""):
                fc["Confidence"] = fc["Confidence"] + Confidence
                fc["Mentions"] = fc["Mentions"] + cntry[country_boosted]
                CountryAlreadyFound = True
        if CountryAlreadyFound == False:
            FoundCountry.append({"Country": country_boosted, "Page": PageName, "Confidence": Confidence,"Mentions":cntry[country_boosted]})
            for c in cntry:
                if c == country_boosted:
                    for ca in cntry:
                        if ca == country_boosted:
                            continue
                        FoundCountry.append({"Country": ca, "Page": PageName, "Confidence": Confidence,"Mentions":cntry[ca]})
    return FoundCity,FoundCountry

def WriteToDB(City,Country,ProjectId,Confidence,Location,Version,cursor,db,database_country):
    sql = None
    if database_country!="":
        if database_country == Country:
            if City != "":
                sql = "UPDATE  ProjectLocation SET City='{0}',DataTrace='{1}',Confidence={2},FoundWhere='{3}' WHERE Projects_idProjects={4} and Country='{5}';".format(City," City text mined, Country from datasource",Confidence,Location,ProjectId,original_database_cntry)
        if database_country!=Country:
            if Country in database_country:
                sql = "UPDATE  ProjectLocation SET City='{0}',DataTrace='{1}',Confidence={2},FoundWhere='{3}' WHERE Projects_idProjects={4} and Country='{5}';".format(
                    City, " City text mined, Country from datasource", Confidence, Location, ProjectId,
                    original_database_cntry)
            else:
                print("Country conflict in project:"+str(ProjectId))
    else:
        sql = "Insert into ProjectLocation (Type,City,Country,Projects_idProjects,Original_idProjects,IsLocationFromDataset,Confidence,FoundWhere,Version)" \
          "Values ('{0}','{1}','{2}',{3},{4},0,{5},'{6}','{7}')".format("Main",City,Country,ProjectId,ProjectId,Confidence,Location,Version)
    if sql!=None:
        cursor.execute(sql)
        db.commit()

def processDatabaseCountry(country):
    if country == "USA":
        country = "United States"
    if country == "UK":
        country = "United Kingdom"
    if "UK" in country:
        country = country.replace("UK","United Kingdom")
    return country

csvfile = open('locations_final_fin4.csv', 'w')
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
sql_projects = "Select idProjects,ProjectName,ProjectWebpage from Projects where Exclude = 0 and idProjects>6804"
cursor.execute(sql_projects)
results = cursor.fetchall()
#csvfile = open('locations_tab2.csv', 'w')
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
st_tagger = StanfordTagger('../Resources')
for row in results:
    idProject = row[0]
    print("Project ID:"+str(idProject))
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
    if (database_city==None or database_city=="" or database_city==" ") and(database_country==None or database_country==" " or database_country==""):
        continue
        original_database_cntry = ""
        database_country = ""
        database_city = ""
    else:
        original_database_cntry = database_country
        database_country = processDatabaseCountry(database_country)
    documents = mongo_db.crawl20190109.find(
        {"mysql_databaseID": str(idProject), "page_title": {"$regex": "([C|c]ontact)"}},
        no_cursor_timeout=True).batch_size(100)
    page_at = "Contact"
    projectText = ""
    for doc in documents:
        text = doc['text']
        projectText = projectText + " " + text
    projectText = checkEngAndTranslate(projectText)
    country_boosted = ""
    city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText, st_tagger,countries)
    print(city)
    print(country)
    print(country_boosted)
    print(page_at)
    if city!="" and city!="uk":
        FoundCity.append({"City":city,"Page":"Contact","Confidence":10,"Mentions":ct[city]})
        for c in ct:
            if c == city:
                for ca in ct:
                    if ct[ca]==ct[c]:
                        FoundCity.append({"City": city, "Page": "Contact", "Confidence": 10,"Mentions":ct[city]})
    if country_boosted!="":
        FoundCountry.append({"Country":country_boosted,"Page":"Contact","Confidence":10,"Mentions":cntry[country_boosted]})
        for c in cntry:
            if c == country_boosted:
                for ca in cntry:
                    if cntry[ca]==cntry[c]:
                        FoundCity.append({"Country": ca, "Page": "Contact", "Confidence": 10,"Mentions":cntry[country_boosted]})

    if len(FoundCity)>0 and len(FoundCountry)>0:
        try:
            c, cn, conf = findBestMatch(FoundCity, FoundCountry,database_country)
            WriteToDB(c.title(), cn, idProject, 10, "Contact", "v1", cursor, db, database_country)
            writer.writerow([idProject,projectName,c.title(),cn,database_city,database_country,10,"Contact",projectWebpage])
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
    city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText,st_tagger,countries)
    print(city)
    print(country)
    print(country_boosted)
    print(page_at)

    ######################################
    FoundCity,FoundCountry = AddRelevantLocationsToList(city,country_boosted,FoundCity,FoundCountry,8,"About")
    ####################################

    c,cn,conf = findBestMatch(FoundCity,FoundCountry,database_country)
    if c!="" and cn!="":
        try:
            WriteToDB(c.title(), cn, idProject, 10, "About", "v1", cursor, db, database_country)
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
    city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText, st_tagger,countries)
    print(city)
    print(country)
    print(country_boosted)
    print(page_at)

    ######################################
    FoundCity, FoundCountry = AddRelevantLocationsToList(city, country_boosted, FoundCity, FoundCountry, 6, "Description")
    ####################################
    c,cn,conf = findBestMatch(FoundCity,FoundCountry,database_country)
    if c!="" and cn!="":
        print(c)
        print(cn)
        print(database_city)
        try:
            WriteToDB(c.title(), cn, idProject, conf, "Description", "v1", cursor, db, database_country)
            writer.writerow(
            [idProject, projectName, c.title().encode('utf-8'), cn.encode('utf-8'), database_city, database_country.encode('utf-8'),
            conf, "Description",projectWebpage.encode('utf-8')])
        except:
            print("Problem 12")
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
        city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText, st_tagger,countries)
        print(city)
        print(country)
        print(country_boosted)
        print(page_at)

        ######################################
        FoundCity, FoundCountry = AddRelevantLocationsToList(city, country_boosted, FoundCity, FoundCountry, 4,
                                                             "One page")
        ####################################
        c, cn, conf = findBestMatch(FoundCity, FoundCountry,database_country)
        if c != "" and cn != "":
            try:
                WriteToDB(c.title(), cn, idProject, conf, "One page", "v1", cursor, db, database_country)
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
            city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText, st_tagger,countries)
            print(city)
            print(country)
            print(country_boosted)
            print(page_at)
            ######################################
            FoundCity, FoundCountry = AddRelevantLocationsToList(city, country_boosted, FoundCity, FoundCountry, 2,
                                                                 "Main page")
            ####################################
            c, cn, conf = findBestMatch(FoundCity, FoundCountry,database_country)
            if c != "" and cn != "":
                try:
                    WriteToDB(c.title(), cn, idProject, conf, "Main page", "v1", cursor, db, database_country)
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
    city, country, country_boosted,st_tagger,ct,cntry = FindLocation(projectText, st_tagger,countries)
    print(city)
    print(country)
    print(country_boosted)
    print(page_at)

    ######################################
    FoundCity, FoundCountry = AddRelevantLocationsToList(city, country_boosted, FoundCity, FoundCountry, 1,
                                                         "General")
    ####################################
    c, cn, conf = findBestMatch(FoundCity, FoundCountry,database_country)
    if c != "" and cn != "":
        try:
            WriteToDB(c.title(), cn, idProject, conf, "General", "v1", cursor, db, database_country)
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
            WriteToDB(c.title(), cn, idProject, conf, "AfterAll", "v1", cursor, db, database_country)
            writer.writerow(
            [idProject, projectName, c.title(), cn, database_city, database_country,
            0.5, "AfterAll", projectWebpage, ])
    except:
        print("Sort of a problem")
csvfile.close()