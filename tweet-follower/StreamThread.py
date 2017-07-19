import threading
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import MySQLdb
from my_settings import *
import json


db = MySQLdb.connect(host,username,password,database,charset='utf8')

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    global followList
    def __init__(self,listToFollow):
        global followList
        self.followList = listToFollow
        self.Stop = False

    def on_data(self, data):
        parsed_json = json.loads(data)
        created_at = parsed_json['created_at']
        text = parsed_json['text']
        screen_name = parsed_json['user']['screen_name']
        retweet_count = parsed_json['retweet_count']
        favorite_count = parsed_json['favorite_count']
        #cursor = db.cursor()
        print(text)
        #sql = "INSERT into tweets (date,tweet_text,user,retweetcount,favor_count) values (NOW(),'%s','%s','%s',%d,%d)" % (text,screen_name,int(retweet_count),int(favorite_count))
        try:
            print("End")
            #cursor.execute(sql)
            #print(sql)
            #db.commit()
        except Exception:
            print("Something went wrong")
        if (self.Stop==True):
            return False
        else:
            return True

    def on_error(self, status):
        print(status)

class StreamThread(threading.Thread):
    def __init__(self,keywordToFollow):
        super(StreamThread, self).__init__()
        self._stop_event = threading.Event()
        self.keyword = keywordToFollow
        self.listener = None

    def run(self):
        listToFollow = []
        listToFollow.append(self.keyword)
        self.listener = StdOutListener(listToFollow)
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = Stream(auth, self.listener)
        print("starting following "+self.keyword)
        stream.filter(track=listToFollow, async=True)

    def stop(self):
        self._stop_event.set()
        self.listener.Stop = True



    def stopped(self):
        return self._stop_event.is_set()
