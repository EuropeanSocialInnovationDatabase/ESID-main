from my_settings import *
from tweepy import OAuthHandler,API

if __name__ == '__main__':
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    user = api.get_user(id="dreadknight011")
    user_id = user.screen_name
    user_desc = user.description
    user_created = user.created_at
    user_fav_cnt = user.favourites_count
    user_follower_cnt = user.followers_count
    user_friends_cnt = user.friends_count
    user_tw_id = user.id_str
    user_lng = user.lang
    user_listerd_cnt = user.listed_count
    user_location = user.location
    user_name = user.name
    user_statuses_cnt = user.statuses_count
    user_url = user.url

    timeline = api.user_timeline(id="dreadknight011")
    for status in timeline:
        print status.text