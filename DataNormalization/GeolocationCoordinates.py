#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
from database_access import *
import csv

db = MySQLdb.connect(host, username, password, database, charset='utf8')
db2 = MySQLdb.connect(host, username, password, "Semanticon", charset='utf8')
cursor = db.cursor()
cursor2 = db2.cursor()
print("Selecting projects from mysql")
sql_projects = "Select idProjects,ProjectName,ProjectWebpage, City, Country, Longitude, Latitude from Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and Longitude is Null and Latitude is Null and City is not Null and City <> ''"
cursor.execute(sql_projects)
results = cursor.fetchall()
csvfile = open('locations.csv', 'w')
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
    Longitude = None
    Latitude = None
    new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Country_CountryName='{1}';".format(projectCity.encode('utf-8'),ProjectCountry.encode('utf-8'))
    #print new_sql
    cursor2.execute(new_sql)
    results2 = cursor2.fetchall()
    FoundCity = ""
    FoundCountry= ""
    for r in results2:
        FoundCity = r[0]
        FoundCountry = r[1]
        Longitude = r[2]
        Latitude = r[3]
    if len(results2)==0:
        new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Country_CountryName='{1}';".format(
            projectCity.split(',')[0].encode('utf-8'), ProjectCountry.encode('utf-8'))
        #print new_sql
        cursor2.execute(new_sql)
        results2 = cursor2.fetchall()
        FoundCity = ""
        FoundCountry = ""
        for r in results2:
            FoundCity = r[0]
            FoundCountry = r[1]
            Longitude = r[2]
            Latitude = r[3]
        if len(results2) == 0:
            new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0".format(
                projectCity.split(',')[0].encode('utf-8'), ProjectCountry.encode('utf-8'))
            #print new_sql
            cursor2.execute(new_sql)
            results2 = cursor2.fetchall()
            FoundCity = ""
            FoundCountry = ""
            found = False
            for r in results2:
                if found == False:
                    found = True
                else:
                    continue
                FoundCity = r[0]
                FoundCountry = r[1]
                Longitude = r[2]
                Latitude = r[3]
        if len(results2) == 0:
            new_sql = "SELECT City,Country_CountryName,Longitude,Latitude FROM Semanticon.City where city like '{0}' and Population>0".format(
                projectCity.split('-')[0].encode('utf-8'), ProjectCountry.encode('utf-8'))
            #print new_sql
            cursor2.execute(new_sql)
            results2 = cursor2.fetchall()
            FoundCity = ""
            FoundCountry = ""
            found = False
            for r in results2:
                if found == False:
                    found = True
                else:
                    continue
                FoundCity = r[0]
                FoundCountry = r[1]
                Longitude = r[2]
                Latitude = r[3]


    writer.writerow([idProject,projectName.encode('utf-8'),projectWebpage,projectCity.encode('utf-8'),ProjectCountry.encode('utf-8'),Longitude,Latitude,FoundCity.encode('utf-8'),FoundCountry.encode('utf-8')])
    if Longitude == None:
        Longitude = "Null"
    if Latitude == None:
        Latitude = "Null"
    update_sql = "Update ProjectLocation set Longitude={0}, Latitude={1},Country='{2}' where Projects_idProjects={3};".format(Longitude,Latitude,ProjectCountry.encode('utf-8'),idProject)
    print update_sql
    cursor.execute(update_sql)
    db.commit()


