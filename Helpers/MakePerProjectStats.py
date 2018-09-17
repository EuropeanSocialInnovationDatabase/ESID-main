#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import MySQLdb
from database_access import *
import smtplib
from q_email import *
import datetime
import csv


if __name__ == '__main__':
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_email, my_password)
    client = MongoClient()
    db = client.ESID
    dba = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = dba.cursor()
    csvfile = open('project_stats.csv','wb')
    csvwriter = csv.writer(csvfile,delimiter=",",quotechar='"',quoting=csv.QUOTE_MINIMAL)
    sql = "Select * from Projects"
    cursor.execute(sql)
    results = cursor.fetchall()
    csvwriter.writerow(["Project id","ProjectName","Project","Exclude","hasWeb","HasMoreThen350char","HasDescMoreThen350char","hasMoreThen500char","hasCountry","hasCity","hasActor"])
    for res in results:

        project_id = res[0]
        print("Processing project:"+str(project_id))
        is_project = 1
        project_name = res[2]
        project_web = res[11]
        has_wesite = 1
        if project_web==None or project_web == "" or project_web == "Null":
            has_wesite = 0
        exclude = res[19]
        number_chars_t = 0
        number_chars_wb = 0
        number_chars_ot = db.crawl20180801_translated.find(
            {"mysql_databaseID": str(project_id)})
        for itm in number_chars_ot:
            number_chars_t = itm.get('translationLen')
        number_chars_owb = db.crawl20180801_wayback_translated.find(
            {"mysql_databaseID": str(project_id)})
        for itm in number_chars_owb:
            number_chars_wb = itm.get('translationLen')
        sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Value<>'' and Projects_idProjects="+str(project_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        des_text = ""
        for res in results:
            des_text = des_text+" "+res[2]
        total_num_char = number_chars_t + number_chars_wb + len(des_text)
        has_more_350 = 0
        has_more_350 = 0
        if total_num_char>350:
            has_more_350 = 1
        if total_num_char>500:
            has_more500 = 1
        has_desc_over350 = 0
        if len(des_text)>350:
            has_desc_over350 = 1
        has_country = 0
        has_city = 0
        has_actor_linked = 0
        sql = "SELECT * FROM EDSI.ProjectLocation where Projects_idProjects=" + str(project_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            if res[5]!='' and res[5]!=None and res[5]!='Null':
                has_country = 1
            if res[4]!='' and res[4]!=None and res[4]!='Null':
                has_city = 1
        sql = "SELECT  * FROM EDSI.Actors_has_Projects where Projects_idProjects=" + str(project_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            if res[0]!=0:
                has_actor_linked = 1
        csvwriter.writerow(
            [project_id, project_name.encode('utf-8'),is_project,exclude,has_wesite,has_more_350,has_desc_over350,has_more500,has_country,has_city,has_actor_linked])

    csvfile.close()






