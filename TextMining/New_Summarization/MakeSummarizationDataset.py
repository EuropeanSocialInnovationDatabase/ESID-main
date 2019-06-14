#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import MySQLdb
from database_access import *

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID

sql= "SELECT * from EDSI.Projects where KNOWMAK_ready=1"
cursor.execute(sql)
projects = cursor.fetchall()
for pro in projects:
    project_id = pro[0]

    project_data = {}
    project_data['Knowmak_ready'] = 1
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
        project_id)
    cursor.execute(q3)
    descriptions = cursor.fetchall()
    project_data['Descriptions'] = []
    for description in descriptions:
        project_data['Descriptions'].append(description[2])
    if len(project_data['Descriptions']) == 0:
        if project_data['Knowmak_ready'] == 1:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
                project_id)
        else:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v2%'".format(
                project_id)
        cursor.execute(q3)
        descriptions = cursor.fetchall()

        for description in descriptions:
            project_data['Descriptions'].append(description[2])
    if len(project_data['Descriptions']) == 0:
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
            project_id)
        cursor.execute(q3)
        descriptions = cursor.fetchall()
        project_data['Descriptions'] = []
        for description in descriptions:
            project_data['Descriptions'].append(description[2])
    desc = ""
    for description in project_data['Descriptions']:
        desc = desc + description
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                       no_cursor_timeout=True).batch_size(100)
    for doc in documents:
        project_text = doc['translation'].encode('utf-8').strip()
    if len(desc)>100 and len(project_text)>len(desc)*2:
        f = open("Data/Summaries/"+str(project_id)+".txt","w")
        f.write(desc.encode("utf-8").strip())
        f.close()
        e =open("Data/OrigData/"+str(project_id)+".txt","w")
        e.write(project_text)
        e.close()



