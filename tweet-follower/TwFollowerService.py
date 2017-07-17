from flask import Flask
from flask import render_template,request
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

@app.route('/add',methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        result = request.form
        keywords =  result['keywords'].split('\n')
        keywords_comment = result['keywords_comment']
        users = result['users'].split('\n')
        keywords_comment = result['users_comment']

if __name__ == '__main__':
    app.run(host= '0.0.0.0')