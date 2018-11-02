import requests
from flask import Blueprint, render_template
from flask import request
import json

from werkzeug.utils import redirect
from extensions import mysql

conn = mysql.connect()
cursor = conn.cursor()
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
    search_query = request.form['search']
    q = "Select * from Projects where ProjectName like '%{0}%' and Exclude=0".format(search_query)
    cursor.execute(q)
    project_list = cursor.fetchall()

    return render_template('perform_search.html',query = search_query,projects = project_list)

@webpage.route('/project_view/<id>', methods=['GET','POST'])
def project_view(id):
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

    return render_template('project_view.html',project = project_data)


@webpage.route('/suggest_related_project', methods=['POST'])
def suggest_related_project():
    related_id = request.form['project_id']
    return render_template('suggest_related.html',related_project= related_id)

@webpage.route('/error', methods=['POST','GET'])
def error():
    return render_template('error.html')


