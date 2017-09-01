#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

from database_access import *
import MySQLdb
import sys
import simplejson
import datetime

if __name__ == '__main__':
    print "Transforming Social Enterprise UK data"
    fname = "SocialEnterpriseUK.json"

    with codecs.open(fname,"rb",encoding='utf-8') as f:
        se_data = f.read()
    print se_data
    json_data = simplejson.loads(se_data)
    organisation_type = "Non-profit or Social Enterprise"
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()


    #sql = "INSERT INTO DataSources(`Name`, `Type`, 'URL', DataIsOpen, RelatedToEU, AssociatedProject, " \
    #      "Theme, CountryCoverage, SocialInnovationDef, MainEntities, DataSource,InclusionCriteria) VALUES('Digital Social Innovation Database', " \
    #      "'Network', 'https://www.socialenterprise.org.uk','Open but not downloadable', 'No', null,  " \
    #      "'social enterprises','all, predominantly UK', null," \
    #      "'Organisations', null, 'voluntary participation');"
    #cursor.execute(sql)
    #db.commit()
    for item in json_data:
        print item
        latitude = item[1][0][0][0]
        longitude = item[1][0][0][1]
        print "Long:"+str(longitude)
        print "Lat:"+str(latitude)
        name = item[5][0][1][0]
        print u"Name:" + name
        post  = item[5][3][0][1][0]
        print u"Post:" + post
        if len(item[5][3])>1:
            website = item[5][3][1][1][0]
            print "Web:"+str(website)
        else:
            website = ""
        sql_org = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,ActorWebsite," \
                  "DataSources_idDataSources) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql_org, (name, 'S', organisation_type,
                                 'Social Enterprise UK',
                                 website,  2))
        org_id_inTable = cursor.lastrowid
        database_id = org_id_inTable
        db.commit()
        sql_loc = "Insert into Location (Type,Address,Longitude,Latitude,Actors_idActors) VALUES " \
                  "(%s,%s,%s,%s,%s)"
        cursor.execute(sql_loc,("Headquarters",post,
                                longitude,latitude,database_id))
        db.commit()


