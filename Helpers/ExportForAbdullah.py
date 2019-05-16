import MySQLdb
from database_access import *
import csv
import sys
import os

if __name__ == '__main__':
    output_path = sys.argv[1]
    dba = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = dba.cursor()
    print(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    sql = "SELECT distinct(idProjects),ProjectName,DateStart,DateEnd,ProjectWebpage FROM Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude =0 and KNOWMAK_ready=1"
    cursor.execute(sql)
    results = cursor.fetchall()
    projects = []
    pro_file = open(output_path + "/projects_abdullah_1.csv", 'wb')
    pro_writer = csv.writer(pro_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    pro_writer.writerow(["SIP_ID","Title","Website","City","Country","ObjectiveScore","ActorScore","OutputScore","InnovativenessScore","Description"])
    for pro in results:
        projects.append(pro)
        if pro[4] == None:
            web = ""
        else:
            web = pro[4].encode('utf-8')

        sql11 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects="+str(pro[0])
        cursor.execute(sql11)
        Objective = 0
        Actors = 0
        Outputs = 0
        Innovativeness = 0
        results11 = cursor.fetchall()
        for res11 in results11:
            Objective = res11[2]
            Actors = res11[3]
            Outputs = res11[1]
            Innovativeness = res11[4]

        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
            pro[0])
        cursor.execute(q3)
        descriptions = cursor.fetchall()
        Descriptions = []
        for description in descriptions:
            Descriptions.append(description[2])
        if len(Descriptions) == 0:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
                    pro[0])

            cursor.execute(q3)
            descriptions = cursor.fetchall()

            for description in descriptions:
                Descriptions.append(description[2])
        if len(Descriptions) == 0:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
                pro[0])
            cursor.execute(q3)
            descriptions = cursor.fetchall()
            Descriptions = []
            for description in descriptions:
                Descriptions.append(description[2])
        #pro_writer.writerow([res[0],res[1].encode('utf-8'),res[2],res[3],web,description.encode("utf-8"),Objective,Actors,Outputs,Innovativeness])
        id = pro[0]
        sql = "SELECT Projects_idProjects,City,Country,Longitude,Latitude FROM EDSI.ProjectLocation where Projects_idProjects ="+str(id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            if res[1] == None:
                city = ""
            else:
                city = res[1].encode('utf-8')
            if res[2] == None:
                country = ""
            else:
                country = res[2].encode('utf-8')
        description = ""
        if len(Descriptions)>0:
            description = Descriptions[0]
        project_title = pro[1].encode('utf-8', 'ignore').decode('utf-8')
        website = pro[4]
        city = city.decode('utf-8')
        description = description.encode('utf-8', 'ignore').decode('utf-8')
        country = country.encode('utf-8', 'ignore').decode('utf-8')
        print(pro[0])
        pro_writer.writerow([pro[0],project_title.encode('utf-8', 'ignore'),website,city.encode('utf-8', 'ignore'),country,Objective,Actors,Outputs,Innovativeness,description.encode('utf-8', 'ignore')])
    pro_file.close()



