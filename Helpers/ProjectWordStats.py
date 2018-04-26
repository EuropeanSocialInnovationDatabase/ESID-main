#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from pymongo import MongoClient
import nltk
import MySQLdb
from database_access import *
import os
import re
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


if __name__ == '__main__':
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    with open('projects_stats.csv', 'wb') as csvfile:
        res2 = csv.writer(csvfile, delimiter=';',
                          quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sql = "Select idProjects,ProjectName,ProjectWebpage,FacebookPage,ProjectTwitter,FirstDataSource from Projects"
        cursor.execute(sql)
        results = cursor.fetchall()
        client = MongoClient()
        db = client.ESID
        urls = []
        for res in results:
            idProject = res[0]
            print(str(idProject))
            ProjectName = res[1]
            ProjectWeb = res[2]
            Facebook = res[3]
            Twitter = res[4]
            DataSource = res[5]
            if ProjectWeb == None:
                ProjectWeb = ""
            if Facebook == None:
                Facebook = ""
            if Twitter == None:
                Twitter = ""
            everything = db.translated2.find({"mysql_databaseID":str(idProject)}, no_cursor_timeout=True).batch_size(30)
            project_text = ""
            for pro in everything:
                try:
                    name = pro["name"]
                    # page_title = pro["page_title"]
                    id = pro["mysql_databaseID"]
                    project_text = project_text + "---------------------------------------\r\nNEW PAGE: " + "\r\n\r\n" + \
                                           pro["translation"]
                    project_text = "---------------------------------------\r\nNEW PAGE: " + "\r\n\r\n" + pro[
                            "translation"]
                except:
                    print("Exception: Record ignored")
            sql_des = "SELECT * FROM EDSI.AdditionalProjectData where (FieldName like '%Description%' or FieldName like '%Challenges Addressed%' " \
                      "or FieldName like '%Actor%' or FieldName like '%Impact%' or FieldName like '%Social%' or FieldName like '%Note%' or FieldName like '%Purpose%') and Projects_idProjects=" + str(idProject)
            cursor.execute(sql_des)
            results = cursor.fetchall()
            description = ""
            for res in results:
                description = description + " \n\n" + strip_tags(res[2])
            desc_tokens = nltk.word_tokenize(description)
            text_tokens = nltk.word_tokenize(project_text)
            res2.writerow(
                [str(idProject),ProjectName.encode('utf-8').strip(), ProjectWeb.encode('utf-8').strip(), Facebook, Twitter, DataSource,len(text_tokens),len(desc_tokens)])



    print("Done")