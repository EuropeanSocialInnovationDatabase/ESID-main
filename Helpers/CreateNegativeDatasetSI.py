#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
from database_access import *
from pymongo import MongoClient
import os

import csv

if __name__ == '__main__':
    if not os.path.exists("NegativeDataset"):
        os.makedirs("NegativeDataset")
    output_folder = "NegativeDataset"
    client = MongoClient()
    db = client.ESID
    dbr = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = dbr.cursor()
    cursor.execute("SELECT * FROM EDSI.Projects where Exclude=1")
    results = cursor.fetchall()
    ids_nosite = []
    for res in results:
        ids_nosite.append(str(res[0]))
    everything = db.crawl20180712_translated.find()

    project_set = set()
    for pro in everything:
        print "Checking "+pro['mysql_databaseID']
        if pro["mysql_databaseID"] in ids_nosite:
            f = open(output_folder+"/"+pro["mysql_databaseID"] +".txt")
            f.write(pro["translation"])
            f.write("WHOLE PROJECT MARK")
            f.close()
            f.open(output_folder+"/"+pro["mysql_databaseID"] +".ann")
            f.close()
    print("Done")

