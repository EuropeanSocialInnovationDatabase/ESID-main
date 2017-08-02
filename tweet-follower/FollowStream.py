#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import MySQLdb
import json
from StreamThread import StreamThread
from GetUserDataAndTweets import UserFollowThread
#TODO: TEST Whether GET UserData and Tweets is invoked
from my_settings import *
import time

if __name__ == '__main__':
    fresh_start = True
    print("Hello")
    Threads = []
    cnt = 0
    uft = UserFollowThread()
    uft.start()
    while True:
        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        cursor = db.cursor()
        sql_del = "SELECT * FROM KeyWords where Following=2" #Schedulled to be deleted
        cursor.execute(sql_del)
        results = cursor.fetchall()
        for res in results:
            keywordToDelete = res[1]
            for Th in Threads:
                if Th.keyword == keywordToDelete:
                    Th.stop()
                    Threads.remove(Th)
                    sql2 = "Update KeyWords set Following=3 where KeyWord='" + res[1] + "'" # deleted
                    cursor.execute(sql2)
                    db.commit()
        sql = "SELECT * FROM KeyWords where Following=0"
        if(fresh_start==True):
            fresh_start = False
            sql = sql + " or Following=1"
        cursor.execute(sql)
        results = cursor.fetchall()

        for res in results:
            st = StreamThread(res[1])
            st.start()
            Threads.append(st)
            sql2 = "Update KeyWords set Following=1 where KeyWord='"+res[1]+"'"
            cursor.execute(sql2)
            db.commit()
        if cnt==24*60:
            uft = UserFollowThread()
            uft.start()

        time.sleep(60)
        cnt = cnt + 1
        cursor.close()
        db.close()
