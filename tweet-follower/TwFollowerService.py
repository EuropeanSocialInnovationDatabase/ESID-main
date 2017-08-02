from flask import Flask
from flask import render_template,request
from my_settings import *
import MySQLdb
app = Flask(__name__)

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
    return render_template('view_stats.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/manage_keywords')
def manage_keywords():
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "SELECT * FROM twitter_follow.keywords;"
    cursor.execute(sql)
    result = cursor.fetchall()
    keywords_res = []
    for res in result:
        keyword = KeyWord(res[0],res[1],res[2],res[3],res[4],res[5])
        keywords_res.append(keyword)
    cursor.close()
    db.close()

    return render_template('manage_keywords.html',keywords = keywords_res)

@app.route('/remove_keyword',methods = [ 'GET'])
def remove_keyword():
    id_toRemove = request.args.get("id")
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "UPDATE keywords set Following = 2 where idKeyWords='%s'"
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

class KeyWord:
    def __init__(self, id, keyword,isUser,comment,date,FollowState):
        self.id = id
        self.keyword = keyword
        self.isUser = isUser
        self.comment = comment
        self.date = date
        self.FollowState = FollowState


if __name__ == '__main__':
    app.run(host= '0.0.0.0')