#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jan 24, 2015

@author: Nikola Milosevic

Created at the University of Manchester, School of Computer Science
Licence GNU/GPL 3.0
'''
from __future__ import absolute_import, print_function

import MySQLdb
import json

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from my_settings import *





db = MySQLdb.connect(host,username,password,database,charset='utf8')

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    global followList
    def __init__(self,listToFollow):
        global followList
        followList = listToFollow
    def on_data(self, data):
        parsed_json = json.loads(data)
        created_at = parsed_json['created_at']
        text = parsed_json['text']
        screen_name = parsed_json['user']['screen_name']
        retweet_count = parsed_json['retweet_count']
        favorite_count = parsed_json['favorite_count']
        cursor = db.cursor()
        sql = "INSERT into tweets (date,tweet_text,user,retweetcount,favor_count) values (NOW(),'%s','%s','%s',%d,%d)" % (text,screen_name,int(retweet_count),int(favorite_count))
        try:
            cursor.execute(sql)
            print(sql)
            db.commit()
        except Exception:
            print("Something went wrong")
    def on_error(self, status):
        print(status)
if __name__ == '__main__':
    listToFollow = []
    l = StdOutListener(listToFollow)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    print("starting")
    stream.filter(track=listToFollow)