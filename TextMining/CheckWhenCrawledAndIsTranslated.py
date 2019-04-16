#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import MySQLdb
import time
from database_access import *

from datetime import datetime
from langdetect import detect
from mtranslate import translate
from nltk.metrics.distance import edit_distance
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Project:
    def __init__(self):
        self.name = ""
        self.webpage = ""
        self.first_datasource = ""
        self.first_datasource_id = -1
        self.idProject = -1


if __name__ == '__main__':
    print("Initializing")
    project_list = []
    print("Processing database")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    print("Selecting projects from mysql")
    sql_projects = "Select * from Projects where Exclude=0"
    cursor.execute(sql_projects)
    results = cursor.fetchall()
    print("Initializing Mongo")
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    translationTimeout = 0

    for res in results:
        #project_names.append(res[0])
        print("Reading project "+str(res[0]) )
        number_of_pages = 0
        pro = Project()
        pro.idProject = res[0]
        isTranslated = 0
        DateCrawled = None
        print(pro.idProject)
        project_list.append(pro)
        print("Grabbing documents from Mongo")
        documents = mongo_db.crawl20190109.find({"mysql_databaseID":str(pro.idProject)},no_cursor_timeout=True).batch_size(100)
        project_text = ""
        original_text = ""
        for doc in documents:
            timestamp = doc['timestamp']
            DateCrawled = datetime.fromtimestamp(timestamp).date()
            break
        documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(pro.idProject)},
                                                no_cursor_timeout=True).batch_size(100)
        for doc in documents:
            isTranslated = 1
            break
        if DateCrawled!=None:
            sql = "Update Projects set Translated={0},DateOfLastCrawl='{1}' where idProjects={2}".format(isTranslated,DateCrawled,pro.idProject)
        else:
            sql = "Update Projects set Translated={0} where idProjects={2}".format(isTranslated,
                                                                                                         DateCrawled,
                                                                                                         pro.idProject)
        cursor.execute(sql)
        db.commit()