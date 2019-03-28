import requests
from flask import Blueprint, render_template
from flask import request
import json

from werkzeug.utils import redirect
from extensions import mysql

#conn = mysql.connect()
#cursor = conn.cursor()
webpage = Blueprint('webpage', __name__)

@webpage.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@webpage.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@webpage.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@webpage.route('/user_created', methods=['GET'])
def user_created():
    return render_template('user_created.html')
    #return render_template('register.html')

@webpage.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@webpage.route('/suggest_new_project', methods=['GET'])
def suggest_new_project():
    return render_template('suggest.html')

@webpage.route('/perform_search', methods=['POST'])
def perform_search():
    conn = mysql.connect()
    cursor = conn.cursor()
    search_query = request.form['search']
    q = "Select * from Projects where ProjectName like '%{0}%' and Exclude=0".format(search_query)
    cursor.execute(q)
    project_list = cursor.fetchall()
    projects = []
    for pro in project_list:
        Country = ""
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        cursor.execute(q2)
        locs = cursor.fetchall()
        for loc in locs:
            Country = loc[5]
        q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(pro[0])
        cursor.execute(q2)
        descs = cursor.fetchall()
        Description = ""
        for desc in descs:
            Description = Description+desc[2]+" "
        Description = Description[0:150]+"..."
        projects.append({"id":pro[0],"Name":pro[2],"Country":Country,"Description":Description})
    cursor.close()
    conn.close()
    return render_template('perform_search.html',query = search_query,projects = projects)

@webpage.route('/edit/<id>', methods=['GET','POST'])
def edit_project(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    project_id = id
    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    cursor.execute(q)
    project_list = cursor.fetchall()
    project_data = {}
    for project in project_list:
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[12]
        project_data['Twitter'] = project[13]
        project_data['FirstDataSource'] = project[16]
    project_data['Locations'] = []
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    cursor.execute(q1)
    locations = cursor.fetchall()
    for loc in locations:
        location = {}
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address'] = loc[3]
        location['city'] = loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude'] = loc[10]
        project_data['Locations'].append(location)

    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(
        project_id)
    cursor.execute(q2)
    actors = cursor.fetchall()
    project_data['Actors'] = []
    for actor in actors:
        act = {}
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        project_data['Actors'].append(act)
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%desc%'".format(
        project_id)
    cursor.execute(q3)
    descriptions = cursor.fetchall()
    project_data['Descriptions'] = []
    for description in descriptions:
        project_data['Descriptions'].append(description[2])
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(
        project_id);
    cursor.execute(q4)
    marks = cursor.fetchall()
    for mark in marks:
        project_data['Outputs'] = mark[1]
        project_data['Objectives'] = mark[2]
        project_data['Actors_s'] = mark[3]
        project_data['Innovativeness'] = mark[4]
    q5 = "Select TopicName,TopicScore,KeyWords from Project_Topics where Projects_idProject={0} and Version like '%v4%' order by TopicScore desc limit 10".format(
        project_id);
    cursor.execute(q5)
    topics = cursor.fetchall()
    project_data['Topics'] = []
    for topic in topics:
        if topic[1]>0.7:
            project_data['Topics'].append(topic[0])
    cursor.close()
    conn.close()
    return render_template('project_edit.html', project=project_data)

@webpage.route('/submit_edit', methods=['POST'])
def edit_submit():
    conn = mysql.connect()
    cursor = conn.cursor()
    project_id = request.form['project_id']
    topics_to_exclude = request.form.getlist('topic_checkbox')
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    topics_to_add = request.form.getlist('topic_added_checkbox')
    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    cursor.execute(q)
    project_list = cursor.fetchall()
    project_data = {}
    for project in project_list:
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[12]
        project_data['Twitter'] = project[13]
        project_data['FirstDataSource'] = project[16]



    project_data['Locations'] = []
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    cursor.execute(q1)
    locations = cursor.fetchall()
    for loc in locations:
        location = {}
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address'] = loc[3]
        location['city'] = loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude'] = loc[10]
        project_data['Locations'].append(location)
    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(
        project_id)
    cursor.execute(q2)
    actors = cursor.fetchall()
    project_data['Actors'] = []
    for actor in actors:
        act = {}
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        project_data['Actors'].append(act)
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%desc%'".format(
        project_id)
    cursor.execute(q3)
    descriptions = cursor.fetchall()
    project_data['Descriptions'] = []
    for description in descriptions:
        project_data['Descriptions'].append(description[2])
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(
        project_id);
    cursor.execute(q4)
    marks = cursor.fetchall()
    for mark in marks:
        project_data['SI_Marks_id'] = mark[0]
        project_data['Outputs'] = mark[1]
        project_data['Objectives'] = mark[2]
        project_data['Actors_s'] = mark[3]
        project_data['Innovativeness'] = mark[4]
    Project_name = request.form['project_name']
    user = request.form['user']
    Project_website_f = request.form['project_website']
    Project_facebook = request.form['project_facebook']
    Project_twitter = request.form['project_twitter']
    Address= request.form['project_address']
    City = request.form['project_city']
    Country_f = request.form['project_country']
    Objectives = request.form['objectives_satisfy']
    Actors = request.form['actors_satisfy']
    Outputs = request.form['outputs_satisfy']
    Innovativeness= request.form['innovativeness_satisfy']
    ProjectType = request.form['project_type']
    StartDate_f = request.form['project_date_start']
    EndDate_f = request.form['project_date_end']
    Description = request.form['project_description']
    Comment = request.form['project_comment']
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
    if StartDate_f == '':
        StartDate_f = 'Null'
    if EndDate_f =='':
        EndDate = 'Null'
    if Project_name!=project_data['project_name']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectName',Project_name,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if Project_website_f=='None':
        Project_website_f = None
    if Project_website_f!=project_data['Website']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectWebsite',Project_website_f,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if Project_facebook=='None':
        Project_facebook = None
    if Project_twitter=='None':
        Project_twitter = None
    if Project_facebook!=project_data['Facebook']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','FacebookPage',Project_facebook,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if Project_twitter!=project_data['Twitter']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectTwitter',Project_twitter,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if ProjectType!=project_data['type']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','Type',ProjectType,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if StartDate_f=='None' or StartDate_f=='' or StartDate_f=='Null':
        StartDate_f = None
    if EndDate_f=='None' or EndDate_f=='' or StartDate_f=='Null':
        EndDate_f = None
    if StartDate_f!=project_data['DateStart']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','DateStart',StartDate_f,project_id,Comment)
        cursor.execute(sql)
        conn.commit()
    if EndDate_f!=project_data['DateEnd']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','DateEnd',EndDate_f,project_id,Comment)
        cursor.execute(sql)
        conn.commit()


    try:
        if Objectives!=str(project_data['Objectives']):
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionObjectives',Objectives,project_id,Comment)
            cursor.execute(sql)
            conn.commit()
    except:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionObjectives',
                                                                                        Objectives, project_id, Comment)
        cursor.execute(sql)
        conn.commit()
    try:
        if Outputs!=str(project_data['Outputs']):
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionOutputs',Outputs,project_id,Comment)
            cursor.execute(sql)
            conn.commit()
    except:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionOutputs', Outputs,
                                                                                        project_id, Comment)
        cursor.execute(sql)
        conn.commit()
    try:
        if Actors!=str(project_data['Actors_s']):
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionActors',Actors,project_id,Comment)
            cursor.execute(sql)
            conn.commit()
    except:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionActors', Actors,
                                                                                        project_id, Comment)
        cursor.execute(sql)
        conn.commit()
    try:
        if Innovativeness!=str(project_data['Innovativeness']):
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionInnovativeness',Innovativeness,project_id,Comment)
            cursor.execute(sql)
            conn.commit()
    except:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionInnovativeness',
                                                                                        Innovativeness, project_id,
                                                                                        Comment)
        cursor.execute(sql)
        conn.commit()


    if len(project_data['Locations'])>0 and Address.strip()!=str(project_data['Locations'][0]['address']):
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','Address',Address,project_data['Locations'][0]['id_location'],Comment)
        cursor.execute(sql)
        conn.commit()
    elif len(project_data['Locations']) == 0 and (Address != '' and Address != 'None'):
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'Address', Address,
                                                                                  -1,Comment)
        cursor.execute(sql)
        conn.commit()
    if len(project_data['Locations'])>0 and City.strip()!=project_data['Locations'][0]['city']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','City',City,project_data['Locations'][0]['id_location'],Comment)
        cursor.execute(sql)
        conn.commit()
    elif len(project_data['Locations']) == 0 and (City != '' and City != 'None'):
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'City', City,
                                                                                  -1,Comment)
        cursor.execute(sql)
        conn.commit()
    if len(project_data['Locations'])>0 and Country_f!=project_data['Locations'][0]['country']:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','Country',Country_f,project_data['Locations'][0]['id_location'],Comment)
        cursor.execute(sql)
        conn.commit()
    elif len(project_data['Locations'])==0 and (Country_f!='' and Country_f!='None'):
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'Country', Country_f,
                                                                                  -1,Comment)
        cursor.execute(sql)
        conn.commit()


    for topic in topics_to_add:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        cursor.execute(sql)
        conn.commit()

    for topic in topics_to_exclude:
        sql_sel = "Select * from Project_Topics where Projects_idProject={0} and Version like '%v4%' and TopicName='{1}'".format(project_id,topic)
        cursor.execute(sql_sel)
        entries = cursor.fetchall()
        id_entry = -1
        for ent in entries:
            id_entry = ent[0]

        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'Project_Topics',
                                                                                        'Exclude', 0, id_entry,
                                                                                        Comment)
        cursor.execute(sql)
        conn.commit()


    desc = ""
    for description in project_data['Descriptions']:
        desc = desc + description
    desc = desc.replace('\r','').replace('\n','').replace(' ','')
    orig_desc = Description
    Description = Description.replace('\r','').replace('\n','').replace(' ','')
    if Description!=desc:
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'AdditionalProjectData','Description',orig_desc,-1,Comment)
        cursor.execute(sql)
        conn.commit()
    for act in actors_list:
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources) Values ('{0}','{1}','{2}','{3}')".format(act['Name'],act['Website'],'ManualInput','57')
        cursor.execute(act_sql)
        actor_id = cursor.lastrowid
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors','{4}')".format(
            user, 1, 0, actor_id,Comment)
        cursor.execute(sql_user_log)
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        cursor.execute(act_location_sql)
    for kr in knowmak_ready:
        if kr == 'knowmak_ready':
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            cursor.execute(sql_p)
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('thank_you_project.html')


@webpage.route('/project_view/<id>', methods=['GET','POST'])
def project_view(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    project_id = id

    sq = "SELECT Distinct(TopicName) as tn,Sum(TopicScore)/Count(TopicName) FROM EDSI.Project_Topics where Version like '%v3%' group by tn;"
    cursor.execute(sq)
    means = cursor.fetchall()
    topic_means = {}
    for m in means:
        topic_means[m[0]]=m[1]

    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    cursor.execute(q)
    project_list = cursor.fetchall()
    project_data = {}
    for project in project_list:
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[12]
        project_data['Twitter'] = project[13]
        project_data['FirstDataSource'] = project[16]
    project_data['Locations'] = []
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    cursor.execute(q1)
    locations = cursor.fetchall()
    for loc in locations:
        location = {}
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address']=loc[3]
        location['city']=loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude']=loc[10]
        project_data['Locations'].append(location)

    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(project_id)
    cursor.execute(q2)
    actors = cursor.fetchall()
    project_data['Actors'] = []
    for actor in actors:
        act = {}
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        project_data['Actors'].append(act)
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%desc%'".format(project_id)
    cursor.execute(q3)
    descriptions = cursor.fetchall()
    project_data['Descriptions'] = []
    for description in descriptions:
        project_data['Descriptions'].append(description[2])
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(project_id);
    cursor.execute(q4)
    marks = cursor.fetchall()
    for mark in marks:
        project_data['Outputs']=mark[1]
        project_data['Objectives']=mark[2]
        project_data['Actors_s']=mark[3]
        project_data['Innovativeness']=mark[4]
    q5 = "Select * from Project_Topics where Projects_idProject={0} and Version like '%v3%'".format(project_id)
    cursor.execute(q5)
    topics = cursor.fetchall()
    r_topics = []
    for topic in topics:
        lenght = topic[9]
        score = topic[2]
        topic_name = topic[1]
        if score>0.7:
            r_topics.append({"TopicName":topic[1],"TopicScore1":topic[2],"TopicScore2":topic[3],"Keywords":topic[4]})
    #     keywords = topic[4].split(',')
    #     if len(keywords)<=1:
    #         continue
    #
    #     if lenght>100000:
    #         score = score*10
    #     elif lenght>50000:
    #         score = score*7
    #     elif lenght>30000:
    #         score = score*2
    #     elif lenght>10000:
    #         score = score*1.7
    #
    #     if score>0.7*topic_means[topic_name]:
    #         r_topics.append({"TopicName":topic[1],"TopicScore1":topic[2],"TopicScore2":topic[3],"Keywords":topic[4]})
    r_topics2 = sorted(r_topics, key=lambda k: k['TopicScore1'],reverse=True)
    if len(r_topics2)==0:
        cursor.close()
        conn.close()
        project_data['Topic'] = r_topics2

        return render_template('project_view.html', project=project_data)
    top_topic = r_topics2[0]
    # r_topics3 = []
    # for r_top in r_topics2:
    #     if r_top["TopicScore1"]>0.4*top_topic["TopicScore1"]:
    #         r_topics3.append(r_top)
    r_topics2 = r_topics2[:10]
    project_data['Topic'] = r_topics2
    cursor.close()
    conn.close()
    return render_template('project_view.html',project = project_data)


@webpage.route('/suggest_related_project', methods=['POST'])
def suggest_related_project():
    related_id = request.form['project_id']
    return render_template('suggest_related.html',related_project= related_id)

@webpage.route('/check_projects', methods=['POST','GET'])
def check_projects():
    conn = mysql.connect()
    cursor = conn.cursor()
    q = "Select * from Projects where ReadyForCheck=1 and KNOWMAK_ready=0 and Exclude=0"
    cursor.execute(q)
    project_list = cursor.fetchall()
    projects = []
    for pro in project_list:
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        cursor.execute(q2)
        locs = cursor.fetchall()
        for loc in locs:
            Country = loc[5]
        q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(
            pro[0])
        cursor.execute(q2)
        descs = cursor.fetchall()
        Description = ""
        for desc in descs:
            Description = Description + desc[2] + " "
        Description = Description[0:150] + "..."
        projects.append({"id": pro[0], "Name": pro[2], "Country": Country, "Description": Description})
    cursor.close()
    conn.close()
    return render_template('check_projects.html',projects=projects)

@webpage.route('/knowmak_ready', methods=['POST','GET'])
def knowmak_ready():
    conn = mysql.connect()
    cursor = conn.cursor()
    q = "Select * from Projects where KNOWMAK_ready=1 and Exclude=0"
    cursor.execute(q)
    project_list = cursor.fetchall()
    projects = []
    for pro in project_list:
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        cursor.execute(q2)
        locs = cursor.fetchall()
        for loc in locs:
            Country = loc[5]
        q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(
            pro[0])
        cursor.execute(q2)
        descs = cursor.fetchall()
        Description = ""
        for desc in descs:
            Description = Description + desc[2] + " "
        Description = Description[0:150] + "..."
        projects.append({"id": pro[0], "Name": pro[2], "Country": Country, "Description": Description})
    cursor.close()
    conn.close()
    return render_template('knowmak_ready.html',projects=projects)


@webpage.route('/error', methods=['POST','GET'])
def error():
    return render_template('error.html')


