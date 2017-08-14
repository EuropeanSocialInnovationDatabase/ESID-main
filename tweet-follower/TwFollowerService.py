from flask import Flask
from flask import render_template,request
from my_settings import *
import MySQLdb
app = Flask(__name__)
import KeyWord
import Entity

@app.route('/')
def main():
    user = {'nickname': 'Nikola'}
    title = "Hello World!"
    return render_template('main.html',
                           title=title,
                           user=user)

@app.route('/add_keywords')
def add_keyworkds():
    return render_template('add_keywords.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/view_stats')
def view_stats():
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql= 'SELECT Type,EntityName,count(EntityName) FROM Entities where Type="Hashtag" group by EntityName order by count(EntityName) desc limit 10;'
    cursor.execute(sql)
    hashtags_raw = cursor.fetchall()
    hashtags = []
    users = []
    for hashtag_raw in hashtags_raw:
        hashtag = Entity.Entity(hashtag_raw[0],hashtag_raw[1],hashtag_raw[2])
        hashtags.append(hashtag)
    sql = 'SELECT Type,EntityName,count(EntityName) FROM Entities where Type="User" group by EntityName order by count(EntityName) desc limit 10;'
    cursor.execute(sql)
    users_raw = cursor.fetchall()
    for user_raw in users_raw:
        user = Entity.Entity(user_raw[0],user_raw[1],user_raw[2])
        users.append(user)
    sql = 'SELECT count(*) FROM tweets;'
    cursor.execute(sql)
    tweets_raw = cursor.fetchall()
    total_tweets = 0
    for tweet in tweets_raw:
        total_tweets = tweet[0]

    return render_template('view_stats.html',users = users,hashtags = hashtags,tweets_cnt = total_tweets)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/manage_keywords')
def manage_keywords():
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "SELECT * FROM KeyWords;"
    cursor.execute(sql)
    result = cursor.fetchall()
    keywords_res = []
    for res in result:
        keyword = KeyWord.KeyWord(res[0],res[1],res[2],res[3],res[4],res[5])
        keywords_res.append(keyword)
    cursor.close()
    db.close()

    return render_template('manage_keywords.html',keywords = keywords_res)

@app.route('/remove_keyword',methods = [ 'GET'])
def remove_keyword():
    id_toRemove = request.args.get("id")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "UPDATE KeyWords set Following = 2 where idKeyWords='%s'"
    cursor.execute(sql, id_toRemove)
    cursor.commit()
    cursor.close()
    db.close()

@app.route('/add',methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        result = request.form
        keywords =  result['keywords'].split('\n')
        keywords_comment = result['keywords_comment']
        users = result['users'].split('\n')
        users_comment = result['users_comment']
        cursor = db.cursor()
        try:
            for key in keywords:
                sql = "INSERT into KeyWords (KeyWord,IsUserHandle,Comment,DateTime,Following) values ('%s','%d','%s',NOW(),'%d')" % (
                key,0 ,keywords_comment, 0)

                cursor.execute(sql)
                #print(sql)
                db.commit()
            for user in users:
                sql = "INSERT into KeyWords (KeyWord,IsUserHandle,Comment,DateTime,Following) values ('%s','%d','%s',NOW(),'%d')" % (
                    user, 1, users_comment, 0)
                cursor.execute(sql)
                # print(sql)
                db.commit()
        except Exception:
            print("Something went wrong")
    cursor.close()
    db.close()
    return render_template('success.html')




if __name__ == '__main__':
    app.run(host= '0.0.0.0')