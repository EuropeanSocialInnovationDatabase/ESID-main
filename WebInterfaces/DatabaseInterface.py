from flask import Flask, send_file
from flask import render_template,request
from my_settings import *
import MySQLdb
app = Flask(__name__)

@app.route('/')
def main():
    user = {'nickname': 'Nikola'}
    title = "Hello World!"
    return render_template('add_project.html',
                           title=title,
                           user=user)

class Organisation:
    def __init__(self):
        self.name = ""
        self.address = ""
        self.country = ""
        self.website = ""

@app.route('/add',methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        result = request.form
        project_name =  result['project_name']
        start_date = result['start_date']
        if start_date == '':
            start_date = "NULL"
        else:
            start_date = "'" + result['start_date'] + "'"
        end_date = result['end_date']
        if end_date == "":
            end_date = "NULL"
        else:
            end_date = "'" + result['end_date'] + "'"
        keydict = result.to_dict(flat=False).keys()
        num_orgs = 0
        organisations = []
        for key in keydict:
            if "org_name_" in key:
                str_num = key.split("_")[2]
                if (num_orgs<int(str_num)):
                    num_orgs = int(str_num)
        if num_orgs>0:
            for i in range(1,num_orgs+1):
                org = Organisation()
                org.name = result['org_name_'+str(i)]
                org.address = result['org_address_' + str(i)]
                org.country = result['org_country_' + str(i)]
                org.website = result['org_website_' + str(i)]
                organisations.append(org)


        project_website = result['project_website']
        project_website2 = result['project_website1']
        project_website3 = result['project_website2']
        project_facebook = result['project_facebook']

        project_twitter = result['project_twitter']
        project_linkedin = result['project_linkedin']
        data_source = result['data_source']
        location_type = result['location_type']
        location_address = result['location_address']
        location_city = result['location_city']
        location_country = result['location_country']
        location_postcode = result['location_postcode']
        location_longitude = result['location_longitude']
        if location_longitude == '':
            location_longitude = "NULL"
        location_latitude = result['location_latitude']
        if location_latitude == "":
            location_latitude = "NULL"
        description = result['description']
        tags = result['tags']

        cursor = db.cursor()
        try:
            data_source_sql = "SELECT * FROM EDSI.DataSources where Name like '%{0}%'".format(data_source)
            cursor.execute(data_source_sql)
            results = cursor.fetchall()
            id_source = -1
            for res in results:
                id_source =  res[0]

            if id_source == -1:
                new_datasource_sql = "INSERT INTO EDSI.DataSources (Name) VALUES ('{0}')".format(data_source)
                cursor.execute(new_datasource_sql)
                db.commit()
                id_source = cursor.lastrowid
            new_project = "INSERT INTO EDSI.Projects (ProjectName,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,ProjectLinkedIn,FirstDataSource,DataSources_idDataSources)" \
                          " VALUE ('{0}',{1},{2},'{3}','{4}','{5}','{6}','{7}',{8})".format(project_name,start_date,end_date,project_website,project_facebook,project_twitter,project_linkedin,data_source,id_source)
            cursor.execute(new_project)
            db.commit()
            id_project = cursor.lastrowid
            if (location_address!='' or location_city!='' or location_country!='' or location_postcode!='' or location_longitude!='NULL' or location_latitude!='NULL'):
                new_location = "Insert into EDSI.ProjectLocation (Type,Address,City,Country,PostCode,Longitude,Latitude,Projects_idProjects) Values " \
                               "('{0}','{1}','{2}','{3}','{4}',{5},{6},{7})"\
                    .format(location_type,location_address,location_city,location_country,location_postcode,location_longitude,location_latitude,id_project)
                cursor.execute(new_location)
                db.commit()
            if (description !=''):
                description_sql = "INSERT INTO EDSI.AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) Values" \
                                  "('{0}','{1}',{2},NOW(),'{3}')".format("Description",description,id_project,"Manual")
                cursor.execute(description_sql)
                db.commit()
            if (project_website2 != ''):
                website_sql = "INSERT INTO EDSI.AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) Values" \
                                  "('{0}','{1}',{2},NOW(),'{3}')".format("Additional WebSource", project_website2, id_project, "Manual")
                cursor.execute(website_sql)
                db.commit()
            if (project_website3 != ''):
                website_sql = "INSERT INTO EDSI.AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) Values" \
                                  "('{0}','{1}',{2},NOW(),'{3}')".format("Additional WebSource", project_website3, id_project, "Manual")
                cursor.execute(website_sql)
                db.commit()
            if (tags != ''):
                tags_sql = "INSERT INTO EDSI.AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) Values" \
                                  "('{0}','{1}',{2},NOW(),'{3}')".format("Tags", tags, id_project, "Manual")
                cursor.execute(tags_sql)
                db.commit()
            for org in organisations:
                actor_sql = "INSERT INTO EDSI.Actors (ActorName,ActorWebsite,DataSources_idDataSources) Values" \
                           "('{0}','{1}','{2}')".format(org.name, org.website, id_source)
                cursor.execute(actor_sql)
                db.commit()
                id_actor = cursor.lastrowid
                actor_loc_sql = "INSERT INTO EDSI.ActorLocation (Type,Address,Country,Actors_idActors) Values" \
                            "('{0}','{1}','{2}','{3}')".format("Headquarter", org.address,org.country, id_actor)
                cursor.execute(actor_loc_sql)
                db.commit()
                actor_project_rel = "INSERT INTO EDSI.Actors_has_Projects (Projects_idProjects,Actors_idActors) Values" \
                                "('{0}','{1}')".format(id_project ,id_actor)
                cursor.execute(actor_project_rel)
                db.commit()
            pass
        except Exception as err:
            print err.message
            print("Something went wrong")
    cursor.close()
    db.close()
    return render_template('success.html')

@app.route('/find_locations',methods = ['POST', 'GET'])
def find_locations():
    pass

@app.route('/download/<path>')
def DownloadFile(path=None):
    if path is None:
        print("400")
        return(400)
    else:
        try:
            return send_file(path,as_attachment=True)
        except:
            pass


if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=int("8002"))