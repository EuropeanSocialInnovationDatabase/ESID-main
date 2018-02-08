#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import MySQLdb
from SPARQLWrapper import SPARQLWrapper, JSON
from database_access import  *
import sys

reload(sys)
sys.setdefaultencoding('utf8')
orglist_names = []
with open('../Resources/orgreg_hei_export_.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    a = 0
    for row in spamreader:
        if a<2:
            a = a+1
            continue
        orglist_names.append(row[3])
        orglist_names.append(row[4])
        orglist_names.append(row[6])
        a = a+1
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql_actors = "Select ActorName from Actors"
cursor.execute(sql_actors)
results = cursor.fetchall()
for res in results:
    orglist_names.append(res[0])

sparql = SPARQLWrapper("http://localhost:8890/sparql")
sparql.setReturnFormat(JSON)
query = """PREFIX dbpedia-owl:  <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource>
    PREFIX dbpprop: <http://dbpedia.org/property>
    SELECT DISTINCT ?Organization ?OrgName
    WHERE{ 
       ?Organization rdf:type dbpedia-owl:Organisation.
       ?Organization rdfs:label ?OrgName.
FILTER (lang(?OrgName) = 'en')
    }"""
sparql.setQuery(query)
data = sparql.query().convert()
for binding in data['results']['bindings']:
    orglist_names.append(binding['OrgName']['value'].encode('utf-8'))
ff = open('gazzeteer.txt','w')

for org in orglist_names:
    ff.write(org+'\n')
ff.close()
