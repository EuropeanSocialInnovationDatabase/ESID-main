#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
from database_access import *
from pymongo import MongoClient

import csv

if __name__ == '__main__':
    client = MongoClient()
    db = client.ESID
    dbr = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = dbr.cursor()
    cursor.execute("SELECT * FROM EDSI.Projects where Exclude=0 and (ProjectWebpage='' or ProjectWebpage is null);")
    results = cursor.fetchall()
    ids_nosite = []
    for res in results:
        ids_nosite.append(res[0])
    everything = db.crawl20180712.aggregate([{"$group":{"_id":"$mysql_databaseID","count":{"$sum":1}}}])
    csvfile = open('eggs.csv', 'wb')
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    project_set = set()
    for pro in everything:
        if pro["_id"] not in project_set:
            project_set.add(pro["_id"])
        else:
            print "Duplicate:"+str(pro["_id"])
        #print str(pro["_id"])+" "+str(pro["count"])
        spamwriter.writerow([ str(pro["_id"]),pro["count"]])
    print("Done")

