#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    if not os.path.exists("ESID-data"):
        os.makedirs("ESID-data")
    client = MongoClient()
    db = client.ESID
    project_text = {}
    everything = db.projects3.find({},no_cursor_timeout=True).batch_size(30)
    i = 1
    for pro in everything:
        try:
            name = pro["name"]
            page_title = pro["page_title"]
            id = pro["mysql_databaseID"]
            if id in project_text.keys():
                project_text[id]=project_text[id]+"---------------------------------------\r\nNEW PAGE: "+page_title+ "\r\n\r\n"+pro["text"]
            else:
                project_text[id]="---------------------------------------\r\nNEW PAGE: "+page_title+ "\r\n\r\n"+pro["text"]
            print "item "+str(i)
            i = i+1
        except:
            print "Exception: Record ignored"
    print "Writing files"
    db.projects3.close()
    for item in project_text:
        sql = "SELECT * from Projects where idProjects = "+item
        cursor.execute(sql)
        results2 = cursor.fetchall()
        for res2 in results2:
            project_name = res2[2]
            project_website = res[11]
            project_source = res[15]

        project_text[item] = "PROJECT NAME: "+project_name+"\r\nPROJECT SOURCE: "+project_source+"\r\n"+project_text[item]
        sql_des = "SELECT * FROM EDSI.AdditionalProjectData where (FieldName like '%Description%' or FieldName like '%Challenges Addressed%' " \
                  "or FieldName like '%Actor%' or FieldName like '%Impact%' or FieldName like '%Social%' or FieldName like '%Note%' or FieldName like '%Purpose%') and Projects_idProjects="+item
        cursor.execute(sql_des)
        results = cursor.fetchall()
        for res in results:
            project_text[item] = project_text[item]+" \n\n"+strip_tags(res[2])
        tokens = nltk.word_tokenize(project_text[item])
        if len(tokens)<500 or len(tokens)>10000:
            continue
        project_text[item] = re.sub(r'(\n\s*)+\n+', '\n\n', project_text[item])
        f = open('ESID-data/p_'+item+".txt", 'w')
        f.write(project_text[item].encode('utf-8').strip())  # python will convert \n to os.linesep
        f.write("\r\n WHOLE PROJECT MARK")
        f.close()
        f = open('ESID-data/p_' + item + ".ann", 'w')
        f.close()


    print "Done"