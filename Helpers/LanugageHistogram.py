#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import nltk
import csv
from urlparse import urlparse

if __name__ == '__main__':
    client = MongoClient()
    db = client.ESID
    project_pagecount = {}
    project_wordcount = {}
    everything = db.crawl20180801_translated.find({})
    languages = {}
    for pro in everything:
        if pro['Language'] not in languages.keys():
            languages[pro['Language']]=1
        else:
            languages[pro['Language']] = languages[pro['Language']] + 1

    csv_file = open('languages.csv', 'wb')
    writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for language in languages:
        writer.writerow([language,languages[language]])
    csv_file.close()
    print("Done")

