#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jan 24, 2015

@author: Nikola Milosevic

Created at the University of Manchester, School of Computer Science
Licence GNU/GPL 3.0
'''
from __future__ import absolute_import, print_function
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import MySQLdb
import codecs
import json
host = 'localhost'
username = 'root'
password = 'MountFuji86!'
database = 'social_media_collector'
db = MySQLdb.connect(host,username,password,database,charset='utf8')
# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
# url of my app: https://apps.twitter.com/app/7823732
consumer_key="4zPbYtbw7mLUne03h7ygjXmHq"
consumer_secret="DiKbFLwWUjwAMEr4FLA1fE0EGo4sjKOe7YKvwOhCC38ze1BHZJ"
# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=" 886879366701035520-mSoHKyR42PkTmkbAb5Dn6a0Eyt1Dj6M"
access_token_secret="ejcT7xE9VZfsvcrJnSjskt2fNyeCBpaYmcf0P5XY2ysOg"
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