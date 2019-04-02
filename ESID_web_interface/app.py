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
    conn = mysql.connect()
    cursor = conn.cursor()
    user = request.json['user']
    password = request.json['pass']
    first_name = request.json['first_n']
    last_name = request.json['last_n']
    organization = request.json['organization']
    city = request.json['city']
    country = request.json['country']

    # Check whether user already exists
    cursor.execute("SELECT * FROM Users WHERE username='{0}'".format(user))
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
    cursor.close()
    conn.close()
    print("Successfully created user")
    return "Successfully created user"


@app.route('/get_token', methods=['POST'])
def get_token():
    conn = mysql.connect()
    cursor = conn.cursor()
    user = request.json['user']
    password = request.json['pass']
    salt = "hdhswrnbjJhs32)"
    hashed_pass = hashlib.sha256(
        (password + salt).encode("utf-8")).hexdigest()
    select_query = "SELECT * FROM Users WHERE username='{0}' and Password='{1}' and IsApproved=1".format(user,hashed_pass)
    cursor.execute(
        select_query)
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
        cursor.close()
        conn.close()
        print(token)
        return token
    else:
        cursor.close()
        print("ERROR: User does not exist")
        return "ERROR: User does not exist"


def validate_user(user, token):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM UserToken WHERE User_Username=%s and Token=%s", (user, token))
    has_user = cursor.fetchone()
    cursor.close()
    conn.close()
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
    conn = mysql.connect()
    cursor = conn.cursor()
    # Validate that user is admin
    user = request.json['user']
    token = request.json['token']
    cursor.execute("SELECT IsAdmin FROM Users WHERE username=%s", (user,))
    user_is_admin = cursor.fetchone()

    if bool(user_is_admin[0]) and validate_user(user, token):
        cursor.close()
        conn.close()
        return "Yes"
    else:
        cursor.close()
        conn.close()
        return "No"


@app.route('/logout', methods=['POST'])
def logout():
    conn = mysql.connect()
    cursor = conn.cursor()
    user = request.json['user']
    token = request.json['token']
    if not validate_user(user, token):
        return "User not logged in"
    cursor.execute("DELETE from UserToken WHERE User_Username=%s", (user,))
    conn.commit()
    cursor.close()
    conn.close()
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
    conn = mysql.connect()
    cursor = conn.cursor()
    Project_name = request.form['project_name']
    user = request.form['user']
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    topics_to_add = request.form.getlist('topic_added_checkbox')
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
    Comment = request.form['project_comment']
    if Project_name =='' or Country=='' or Project_website=='':
        return render_template('error.htm')
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
    if StartDate == '':
        StartDate = 'Null'
    if EndDate =='':
        EndDate = 'Null'
    # project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('{0}','{1}',{2},{3},'{4}','{5}','{6}','{7}',{8})"\
    #     .format(Project_name,ProjectType,StartDate,EndDate,Project_website,Project_facebook,Project_twitter,1,'57')
    project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('%s','%s',%s,%s,'%s','%s','%s','%s',%s)" \
                  % (
                  Project_name, ProjectType, StartDate, EndDate, Project_website, Project_facebook, Project_twitter, 1,
                  '57')

    cursor.execute(project_sql)
    project_id = cursor.lastrowid
    location_sql = "Insert into ProjectLocation (Type,Address,City,Country,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}')".format('Main',Address,City,Country,project_id,project_id)
    cursor.execute(location_sql)
    si_marks = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,SourceModel) Values ({0},{1},{2},{3},{4},'{5}')".format(
        Outputs,Objectives,Actors,Innovativeness,project_id,"ManualAnnotationCrowd"
    )
    cursor.execute(si_marks)
    desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('{0}','{1}','{2}',NOW(),'{3}')".format(
        "Description_sum",Description,project_id,"Manual"
    )
    cursor.execute(desc)
    for act in actors_list:
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources) Values ('{0}','{1}','{2}','{3}')".format(act['Name'],act['Website'],'ManualInput','57')
        cursor.execute(act_sql)
        actor_id = cursor.lastrowid
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors')".format(
            user, 1, 0, actor_id)
        cursor.execute(sql_user_log)
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        cursor.execute(act_location_sql)
    sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}','{4}',NOW(),'Projects','{5}')".format(
        user, 1, 0, project_id, project_id,Comment)
    cursor.execute(sql_user_log)

    conn.commit()
    for topic in topics_to_add:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        cursor.execute(sql)
        conn.commit()
    for kr in knowmak_ready:
        if kr == 'knowmak_ready':
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            cursor.execute(sql_p)
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('thank_you_project.html')

@app.route('/submit_related_project', methods=['POST'])
def submit_related_project():
    conn = mysql.connect()
    cursor = conn.cursor()
    Project_id_to_which_is_related = request.form['related_project']
    user = request.form['user']
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    topics_to_add = request.form.getlist('topic_added_checkbox')
    Relationship = request.form['project_relationship']
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
    Comment = request.form['project_description']
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
    if StartDate == '':
        StartDate = 'Null'
    if EndDate =='':
        EndDate = 'Null'
    # project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}',{8})"\
    #     .format(Project_name,ProjectType,StartDate,EndDate,Project_website,Project_facebook,Project_twitter,1,'57')

    project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('%s','%s',%s,%s,'%s','%s','%s','%s',%s)" \
        % (Project_name, ProjectType, StartDate, EndDate, Project_website, Project_facebook, Project_twitter, 1,
                '57')

    cursor.execute(project_sql)
    project_id = cursor.lastrowid
    location_sql = "Insert into ProjectLocation (Type,Address,City,Country,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}')".format('Main',Address,City,Country,project_id,project_id)
    cursor.execute(location_sql)
    si_marks = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,SourceModel) Values ({0},{1},{2},{3},{4},'{5}')".format(
        Outputs,Objectives,Actors,Innovativeness,project_id,"ManualAnnotationCrowd"
    )
    cursor.execute(si_marks)
    desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('{0}','{1}','{2}',NOW(),'{3}')".format(
        "Description_sum",Description,project_id,"Manual"
    )
    cursor.execute(desc)
    for act in actors_list:
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources,user_suggested) Values ('{0}','{1}','{2}','{3}',1)".format(act['Name'],act['Website'],'ManualInput','57')
        cursor.execute(act_sql)
        actor_id = cursor.lastrowid
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors','{4}')".format(
            user, 1, 0, actor_id,Comment)
        cursor.execute(sql_user_log)

        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        cursor.execute(act_location_sql)
    sql_relation = "Insert into Projects_relates_to_Projects (Projects_idProjects,Projects_idProjects1,RelationshipType) VALUES ({0},{1},'{2}')".format(Project_id_to_which_is_related,project_id,Relationship)
    cursor.execute(sql_relation)
    sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}','{4}',NOW(),'Projects','{5}')".format(user,1,0,project_id,project_id,Comment)
    cursor.execute(sql_user_log)
    conn.commit()
    for topic in topics_to_add:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        cursor.execute(sql)
        conn.commit()
    for kr in knowmak_ready:
        if kr == 'knowmak_ready':
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            cursor.execute(sql_p)
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('thank_you_project.html')

if __name__ == "__main__":
    # MySQL configurations
    #conn = mysql.connect()
    #cursor = conn.cursor()
    app.run(debug=True,port=8080,host="0.0.0.0")


