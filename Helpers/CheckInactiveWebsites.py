#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb

import requests
from database_access import *

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()

sql = "SELECT * FROM EDSI.Projects where Exclude = 0"
cursor.execute(sql)
results = cursor.fetchall()

for res in results:
    try:
        print str(res[0]) + "  "+ str(res[11])

        r = requests.get(res[11])
        if(r.status_code>400):
            new_sql = "Update Projects set InactiveWebsite = 1 where idProjects = {0};".format(res[0])
            cursor.execute(new_sql)
            db.commit()
    except:
        new_sql = "Update Projects set InactiveWebsite = 1 where idProjects = {0};".format(res[0])
        cursor.execute(new_sql)
        db.commit()