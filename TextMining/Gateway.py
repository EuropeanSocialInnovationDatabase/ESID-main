from flask import Flask
from flask import render_template,request
from my_settings import *
import sqlite3
import hashlib
import random
import time
app = Flask(__name__)



@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    username = request.values['user']
    password = request.values['pass']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    t = (username, password,)
    c.execute('SELECT * FROM users WHERE username=? and pass=?', t)
    fetched = c.fetchone()
    if fetched==None:
        conn.commit()
        conn.close()
        return "Bad username of password. User with given credentials does not exist"
    else:
        if fetched[2]=="":
            millis = int(round(time.time() * 1000))
            random.seed(millis)
            ra = random.random()*343213
            token = hashlib.sha224("some sting"+username+password+"jdkskdjf"+str(ra)).hexdigest()
            p = (token,username,password,)
            c.execute('UPDATE users set current_token=? where username=? and pass=?',p)
            conn.commit()
            conn.close()
            return token
        else:
            conn.commit()
            conn.close()
            return fetched[2]

def validate_logged_in(security_token):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    t= (security_token,)
    c.execute('SELECT * FROM users WHERE current_token=? ', t)
    fetched = c.fetchone()
    if fetched!=None:
        conn.close()
        return True
    else:
        conn.close()
        return False

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    security_token = request.values['token']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    p = ("",security_token,)
    c.execute('UPDATE users set current_token=? where current_token=?', p)
    conn.commit()
    conn.close()


def initiate():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username text, pass text, current_token text, when_created date)''')
    t = ('user1','pass123',)
    c.execute('SELECT * FROM users WHERE username=? and pass=?', t)
    fetched =  c.fetchone()
    if fetched == None:
        c.execute('''INSERT INTO users (username,pass,current_token,when_created) VALUES ('user1','pass12344','',date('now'))''')
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()



if __name__ == '__main__':
    initiate()
    app.run(host= '0.0.0.0',port=3000)