#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import csv
from database_access import *

if __name__ == '__main__':
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    with open('projects.csv', 'wb') as csvfile:
        res2 = csv.writer(csvfile, delimiter=',',
                          quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sql = "Select idProjects,ProjectName,ProjectWebpage,FacebookPage,ProjectTwitter,FirstDataSource from Projects"
        cursor.execute(sql)
        results = cursor.fetchall()
        urls = []
        for res in results:
            idActor = res[0]
            ArtName = res[1]
            ArtWeb = res[2]
            Facebook = res[3]
            Twitter = res[4]
            DataSource = res[5]
            if ArtWeb == None:
                ArtWeb = ""
            if Facebook == None:
                Facebook = ""
            if Twitter == None:
                Twitter = ""

            res2.writerow([ArtName.encode('utf-8').strip(), ArtWeb.encode('utf-8').strip(),Facebook,Twitter,DataSource])

