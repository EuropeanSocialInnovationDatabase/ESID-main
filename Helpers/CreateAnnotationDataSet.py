#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
import os

if __name__ == '__main__':
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    if not os.path.exists("ESID-data"):
        os.makedirs("ESID-data")
    client = MongoClient()
    db = client.ESID
    project_text = {}
    everything = db.projects2.find({})
    for pro in everything:
        name = pro["name"]
        id = pro["mysql_databaseID"]
        if id in project_text.keys():
            project_text[id]=project_text[id]+" \n\n"+pro["text"]
        else:
            project_text[id]=pro["text"]
    print "Writing files"
    for item in project_text:
        sql = "SELECT * from Projects where idProjects = "+item
        sql_des = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Description%' and Projects_idProjects="+item
        cursor.execute(sql_des)
        results = cursor.fetchall()
        for res in results:
            project_text[item] = project_text[item]+" \n\n"+res[2]
        tokens = nltk.word_tokenize(project_text[item])
        if len(tokens)<500 or len(tokens)>10000:
            continue
        f = open('ESID-data/p_'+item+".txt", 'w')
        f.write(project_text[item].encode('utf-8').strip())  # python will convert \n to os.linesep
        f.close()
        f = open('ESID-data/p_' + item + ".ann", 'w')
        f.close()


    print "Done"