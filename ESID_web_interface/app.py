import time
import datetime
import hashlib
from flask import Flask, jsonify, request, render_template
from database_access import *
from extensions import mysql
import os



app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = username
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = database
app.config['MYSQL_DATABASE_HOST'] = host
mysql.init_app(app)
from webpages import webpage
app.register_blueprint(webpage)



@app.route("/register", methods=['POST'])
def register():
    user = request.json['user']
    password = request.json['pass']
    first_name = request.json['first_n']
    last_name = request.json['last_n']
    organization = request.json['organization']
    city = request.json['city']
    country = request.json['country']

    # Check whether user already exists
    cursor.execute("SELECT * FROM Users WHERE username=%s", (user,))
    has_user = cursor.fetchone()
    if has_user is not None and has_user[0] == user:
        print("User already exists")
        return "User already exists"
    # make hashes
    salt = "hdhswrnbjJhs32)"
    pass_for_storing = hashlib.sha256(
        (password + salt).encode("utf-8")).hexdigest()
    cursor.execute("INSERT INTO Users (username,Password,FirstName,LastName,City,Country,Institution)"
                   "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   (user, pass_for_storing, first_name,last_name,city,country,organization))
    conn.commit()
    print("Successfully created user")
    return "Successfully created user"


@app.route('/get_token', methods=['POST'])
def get_token():
    user = request.json['user']
    password = request.json['pass']
    salt = "hdhswrnbjJhs32)"
    hashed_pass = hashlib.sha256(
        (password + salt).encode("utf-8")).hexdigest()
    cursor.execute(
        "SELECT * FROM Users WHERE username=%s and Password=%s", (user, hashed_pass))
    has_user = cursor.fetchone()
    if has_user is not None:
        millis = int(round(time.time() * 1000))
        token_salt = "dsagggse"
        expiry_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 86400))
        token = hashlib.sha256(
            (user + str(millis) + token_salt).encode("utf-8")).hexdigest()
        cursor.execute("INSERT INTO UserToken (User_username,Token,ExpiryTime,LastUsed) VALUES (%s, %s, %s, NOW() );",
                       (user, token, expiry_time))
        conn.commit()
        print(token)
        return token
    else:
        print("ERROR: User does not exist")
        return "ERROR: User does not exist"


def validate_user(user, token):
    cursor.execute(
        "SELECT * FROM UserToken WHERE User_Username=%s and Token=%s", (user, token))
    has_user = cursor.fetchone()
    if has_user is None:
        return False
    return has_user[2].timestamp() > time.time()


@app.route('/is_logged', methods=['POST'])
def is_logged():
    user = request.json['user']
    token = request.json['token']
    if validate_user(user, token):
        return "Yes"
    else:
        return "No"


@app.route('/is_admin', methods=['POST'])
def is_admin():
    # Validate that user is admin
    user = request.json['user']
    token = request.json['token']
    cursor.execute("SELECT IsAdmin FROM Users WHERE username=%s", (user,))
    user_is_admin = cursor.fetchone()
    if bool(user_is_admin[0]) and validate_user(user, token):
        return "Yes"
    else:
        return "No"


@app.route('/logout', methods=['POST'])
def logout():
    user = request.json['user']
    token = request.json['token']
    if not validate_user(user, token):
        return "User not logged in"
    cursor.execute("DELETE from UserToken WHERE User_Username=%s", (user,))
    conn.commit()
    return "Logged out"


@app.route('/classify_text', methods=['POST'])
def classify():
    user = request.json['user']
    token = request.json['token']
    text = request.json['text']
    if not validate_user(user, token):
        return "User not logged in"
    return ""

@app.route('/submit_project', methods=['POST'])
def submit_new_project():
    Project_name = request.form['project_name']
    Project_website = request.form['project_website']
    Project_facebook = request.form['project_facebook']
    Project_twitter = request.form['project_twitter']
    Address= request.form['project_address']
    City = request.form['project_city']
    Country = request.form['project_country']
    Objectives = request.form['objectives_satisfy']
    Actors = request.form['actors_satisfy']
    Outputs = request.form['outputs_satisfy']
    Innovativeness= request.form['innovativeness_satisfy']
    ProjectType = request.form['project_type']
    StartDate = request.form['project_date_start']
    EndDate = request.form['project_date_end']
    Description = request.form['project_description']
    actors_list = []
    actor_count = int(request.form['counter'])
    if actor_count>0:
        for i in range(0,actor_count):
            Actor_e = {}
            Actor_e['Name'] = request.form['actor_name_'+str(i)]
            Actor_e['Website'] = request.form['actor_website_' + str(i)]
            Actor_e['City'] = request.form['actor_city_' + str(i)]
            Actor_e['Country'] = request.form['actor_country_' + str(i)]
            actors_list.append(Actor_e)
    project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}',{8})"\
        .format(Project_name,ProjectType,StartDate,EndDate,Project_website,Project_facebook,Project_twitter,1,'57')
    cursor.execute(project_sql)
    project_id = cursor.lastrowid
    location_sql = "Insert into ProjectLocation (Type,Address,City,Country,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}')".format('Main',Address,City,Country,project_id,project_id)
    cursor.execute(location_sql)
    si_marks = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,SourceModel) Values ({0},{1},{2},{3},{4},'{5}')".format(
        Outputs,Objectives,Actors,Innovativeness,project_id,"ManualAnnotationCrowd"
    )
    cursor.execute(si_marks)
    desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('{0}','{1}','{2}',NOW(),'{3}')".format(
        "Description",Description,project_id,"Manual"
    )
    cursor.execute(desc)
    for act in actors_list:
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources) Values ('{0}','{1}','{2}','{3}')".format(act['Name'],act['Website'],'ManualInput','57')
        cursor.execute(act_sql)
        actor_id = cursor.lastrowid
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        cursor.execute(act_location_sql)

    conn.commit()
    return render_template('thank_you_project.html')

if __name__ == "__main__":
    # MySQL configurations
    conn = mysql.connect()
    cursor = conn.cursor()
    app.run(debug=True,port=8080)#,host="0.0.0.0")


