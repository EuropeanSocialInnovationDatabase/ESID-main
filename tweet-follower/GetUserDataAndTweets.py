from my_settings import *
from tweepy import OAuthHandler,API
import  threading
import MySQLdb
import KeyWord
import time

class UserFollowThread(threading.Thread):
    def __init__(self ):
        super(UserFollowThread, self).__init__()
        self._stop_event = threading.Event()
        self.listener = None

    def run(self):
        #print("starting following @" + self.user_to_follow)
        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM keywords;"
        cursor.execute(sql)
        result = cursor.fetchall()
        users = []
        for res in result:
            keyword = KeyWord.KeyWord(res[0], res[1], res[2], res[3], res[4], res[5])
            if(keyword.isUser=='1'):
                users.append(keyword)
        for user in users:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = API(auth)
            userObj = api.get_user(id=user.keyword)
            user_desc = userObj.description
            user_created = userObj.created_at
            user_fav_cnt = userObj.favourites_count
            user_follower_cnt = userObj.followers_count
            user_friends_cnt = userObj.friends_count
            user_tw_id = userObj.id_str
            user_screen_name = userObj.screen_name
            user_lng = userObj.lang
            user_listerd_cnt = userObj.listed_count
            user_timezone = userObj.time_zone
            user_location = userObj.location
            user_name = userObj.name
            user_statuses_cnt = userObj.statuses_count
            user_url = userObj.url
            select_sql = 'select * from twusersofinterest where twitterid="'+user_tw_id+'"'
            cursor.execute(select_sql)
            existing_users = cursor.fetchall()
            global inserted_id
            inserted_id = -1
            if(len(existing_users)==0):
                global inserted_id
                sql = 'insert into twusersofinterest (twitterid,name,screenname,description,url,location,timezone,created_at,statuses_count,followers_count,following_count,fav_count,listed_count,following)' \
                  'Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql,(user_tw_id,user_name,user_screen_name,user_desc,user_url,user_location,user_timezone,user_created,user_statuses_cnt,user_follower_cnt,user_friends_cnt,user_fav_cnt,user_listerd_cnt,-1))
                inserted_id = cursor.lastrowid
                db.commit()
            else:
                global inserted_id
                inserted_id = existing_users[0][0]
                sql = 'update twusersofinterest set name=%s,screenname=%s,description=%s,url=%s,location=%s,timezone=%s,created_at=%s,statuses_count=%s,followers_count=%s,following_count=%s,fav_count=%s,listed_count=%s where twitterid=%s'
                cursor.execute(sql, (
                user_name, user_screen_name, user_desc, user_url, user_location, user_timezone,
                user_created, user_statuses_cnt, user_follower_cnt, user_friends_cnt, user_fav_cnt, user_listerd_cnt,user_tw_id))
                db.commit()
            timeline = api.user_timeline(id_str=user_tw_id)
            print "inserted id:"+str(inserted_id)
            for status in timeline:
                status_id = status.id_str
                status_created = status.created_at
                status_text = status.text
                status_in_reply_to_screen_name = status.in_reply_to_screen_name
                status_in_reply_to_tweet_id = status.in_reply_to_status_id_str
                status_retweets = status.retweet_count
                status_favcount = status.favorite_count
                select_sql2 = "select * from usertweets where twitter_id="+status_id
                cursor.execute(select_sql2)
                selected_tweets = cursor.fetchall()
                if(len(selected_tweets)==0):
                    insert_sql = "insert into usertweets (recorded,text,in_reply_to_screenname,in_reply_to_status_id,twitter_id,retweets,fav_count,TwUsersOfInterest_UsersOfInterestId)" \
                                 "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(insert_sql,(status_created,status_text,status_in_reply_to_screen_name,status_in_reply_to_tweet_id,status_id,status_retweets,status_favcount,inserted_id))
                    status_id_inTable=cursor.lastrowid
                    db.commit()
                    hashtags = status.entities['hashtags']
                    for hashtag in hashtags:
                        hash_sql = "insert into usertweetentities (Type,EntityName,UserTweets_idUserTweets) VALUES (%s,%s,%s)"
                        cursor.execute(hash_sql,('Hashtag',hashtag['text'],status_id_inTable))
                        db.commit()
                    usermentions = status.entities['user_mentions']
                    for mentionedUser in usermentions:
                        hash_sql = "insert into usertweetentities (Type,EntityName,UserTweets_idUserTweets) VALUES (%s,%s,%s)"
                        cursor.execute(hash_sql, ("User",mentionedUser['screen_name'], status_id_inTable))
                        db.commit()
                print status.text

        cursor.close()
        db.close()


    def stop(self):
        self._stop_event.set()
        self.listener.Stop = True

    def stopped(self):
        return self._stop_event.is_set()



