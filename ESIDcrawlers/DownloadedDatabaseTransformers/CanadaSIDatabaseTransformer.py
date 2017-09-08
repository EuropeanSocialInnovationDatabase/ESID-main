#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database_access import *
import MySQLdb
import sys
import csv
import datetime

class Organisation:
    def __init__(self):
        self.database_id = -1
        self.organisation_name = "" # ActorName
        self.description = ""# ActorsAdditionalData-ActorLongDescription
        self.province ="" # Location.Country
        self.country = "Canada" #Location.City
        self.impact = ""
        self.notes = ""
        self.contact = ""




if __name__ == '__main__':
    print("Starting CanadianSocialInnovationTransformer")
    if(len(sys.argv)<2):
        print "This scripts needs one arguments: csv with organisations"
        exit(1)
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    organisations_arg = sys.argv[1]
    organisations = []
    with open(organisations_arg, 'rb') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in orgreader:
            if(i==0):
                i+=1
                continue
            org = Organisation()
            org.organisation_name = row[0]
            org.description = row[1]
            org.province = row[2]
            org.impact = row[3]
            org.notes = row[4]
            org.contact = row[5]
            organisations.append(org)
            i+=1
    for organisation in organisations:
        print "Saving "+organisation.organisation_name
        sql_org = "Insert into Actors (ActorName,Type,SourceOriginallyObtained,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql_org, (organisation.organisation_name, 'S',
                                 'Social Innovation Generation (SIG): Social Innovation in Canada database',
                                 6))
        org_id_inTable = cursor.lastrowid
        organisation.database_id = org_id_inTable
        db.commit()

        sql_loc = "Insert into Location (Type,Country,Actors_idActors) VALUES " \
                      "(%s,%s,%s)"
        cursor.execute(sql_loc, ("Headquarters", organisation.country,
                                     organisation.database_id))
        db.commit()

        sql_short_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
        "Description", organisation.description, organisation.database_id, "https://docs.google.com/spreadsheets/d/1fb_riOBF3JEXxX_dnrKAtw_55URbul-1qaYOUDVzVCY/edit#gid=0"))
        db.commit()

        sql_province = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_province, (
            "Province", organisation.province, organisation.database_id,
            "https://docs.google.com/spreadsheets/d/1fb_riOBF3JEXxX_dnrKAtw_55URbul-1qaYOUDVzVCY/edit#gid=0"))
        db.commit()

        sql_impact = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_impact, (
            "Impact", organisation.impact, organisation.database_id,
            "https://docs.google.com/spreadsheets/d/1fb_riOBF3JEXxX_dnrKAtw_55URbul-1qaYOUDVzVCY/edit#gid=0"))
        db.commit()

        sql_notes = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                     "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_notes, (
            "Notes", organisation.notes, organisation.database_id,
            "https://docs.google.com/spreadsheets/d/1fb_riOBF3JEXxX_dnrKAtw_55URbul-1qaYOUDVzVCY/edit#gid=0"))
        db.commit()
        sql_contact = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                     "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_contact, (
            "Contact", organisation.contact, organisation.database_id,
            "https://docs.google.com/spreadsheets/d/1fb_riOBF3JEXxX_dnrKAtw_55URbul-1qaYOUDVzVCY/edit#gid=0"))
        db.commit()
    print "Done!!!!"
