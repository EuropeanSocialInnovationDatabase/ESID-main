#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import isfile, join
from pymongo import MongoClient
import os

import csv

if __name__ == '__main__':
    output_folder = "../ESIDcrawlers/ESIDcrawlers/Crawled"
    onlyfiles = [f for f in os.listdir(output_folder) if isfile(join(output_folder, f))]


    project_set = set()
    for pro in onlyfiles:
        f = open(output_folder+"/"+pro,"r")
        text = f.read()
        f.close()
        f2 = open(output_folder+"/"+pro,"w")
        f2.write(text)
        f2.write("WHOLE PROJECT MARK")
        f2.close()
        f3 = open(output_folder+"/"+pro.replace(".txt",".ann"),'w')
        f3.close()
    print("Done")

