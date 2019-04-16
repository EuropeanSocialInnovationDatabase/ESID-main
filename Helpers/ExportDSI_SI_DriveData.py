#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import MySQLdb
from TextMining.database_access import *
from pymongo import MongoClient
import os
directory = "dsi_si_topics"
if not os.path.exists(directory):
    os.makedirs(directory)
csvfile = open('dsi_si_topics2.csv', 'w')
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(["ProjectID","ProjectName","Website","DataSource","Topics","KNOWMAK topics"])
db = MySQLdb.connect(host, username, password, database, charset='utf8')
db.set_character_set("utf8")
cursor = db.cursor()
sql = "Select * from Projects where Exclude = 0 and (FirstDataSource like '%Digital Social%')"
cursor.execute(sql)
results = cursor.fetchall()
for res in results:
    idProject = res[0]
    print(idProject)
    projectName = res[2]
    projectWeb = res[11]
    dataSource = res[16]
    sql_topics = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and (FieldName like '%Support Tag%' or FieldName like '%Technology%' or FieldName like '%Focus%')".format(idProject)
    cursor.execute(sql_topics)
    ran = cursor.fetchall()
    topics = ""
    for r in ran:
        top = r[2]
        topics = topics + "," + top

    sql_content = "SELECT * FROM EDSI.ProjectCrawls where Projects_idProjects="+str(idProject)
    cursor.execute(sql_content)
    content = cursor.fetchall()
    cnt = ""
    for c in content:
        cnt = cnt + c[2]
    sql_knowmak = "SELECT * FROM EDSI.Project_Topics where Version like '%v4%' and Projects_idProject='"+str(idProject)+"' order by TopicScore desc"
    cursor.execute(sql_knowmak)
    content = cursor.fetchall()
    topics_knowmak= ""
    for topic in content:
        topics_knowmak = topics_knowmak+topic[1]+"("+str(topic[2])+")"+","
    if len(cnt)>300:
        writer.writerow([idProject, projectName.encode('utf-8'), projectWeb, dataSource, topics.encode('utf-8'),topics_knowmak.encode('utf-8')])
        file = open(directory +"/" + str(idProject)+".txt","w")
        file.write(cnt.encode('utf-8'))
        file.close()


