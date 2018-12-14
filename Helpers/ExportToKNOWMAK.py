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
    sql = "SELECT distinct(idProjects),ProjectName,DateStart,DateEnd,ProjectWebpage FROM Projects left join ProjectLocation on idProjects=Projects_idProjects where Exclude =0"
    cursor.execute(sql)
    results = cursor.fetchall()
    projects = []
    pro_file = open(output_path + "/projects.csv", 'wb')
    pro_writer = csv.writer(pro_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    topic_file = open(output_path + "/topics.csv", 'wb')
    topic_writer = csv.writer(topic_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    topic_writer.writerow(["TopicName","TopicScore1","TopicScore2","Keywords","Project_id","TextLength"])
    pro_writer.writerow(["SIP_ID","Title","Start_date","End_date","Website","Description","ObjectiveScore","ActorScore","OutputScore","InnovativenessScore"])

    actor_file = open(output_path + "/actors.csv", 'wb')
    actor_writer = csv.writer(actor_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    actor_writer.writerow(["SIA_ID", "Title", "Webpage"])
    actor_ids = []
    pro_act_file = open(output_path + "/project_actor.csv", 'wb')
    pro_act_writer = csv.writer(pro_act_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    pro_act_writer.writerow(["SIA_ID", "SIP_ID","Role"])
    for res in results:
        projects.append(res)
        if res[4] == None:
            web = ""
        else:
            web = res[4].encode('utf-8')

        sql11 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects="+str(res[0])
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


        sql2 = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects ="+str(res[0])
        cursor.execute(sql2)
        description = ""
        results2 = cursor.fetchall()
        for res2 in results2:
            description = description + " "+res2[2]
        pro_writer.writerow([res[0],res[1].encode('utf-8'),res[2],res[3],web,description.encode("utf-8"),Objective,Actors,Outputs,Innovativeness])

        sql3 = "SELECT Actors_idActors,Projects_idProjects,OrganisationRole FROM EDSI.Actors_has_Projects where Projects_idProjects="+str(res[0])
        cursor.execute(sql3)
        results3 = cursor.fetchall()
        for res3 in results3:
            actor_ids.append(res3[0])
            pro_act_writer.writerow(res3)

        sql4 = "Select * from EDSI.Project_Topics where Version like '%v2%' and Projects_idProject ="+str(res[0])
        cursor.execute(sql4)
        results4 = cursor.fetchall()
        r_topics = []
        for res4 in results4:
            lenght = res4[9]
            score = res4[2]
            if lenght > 100000:
                score = score * 10
            elif lenght > 50000:
                score = score * 7
            elif lenght > 30000:
                score = score * 2
            elif lenght > 10000:
                score = score * 1.7
            if score > 3:
                r_topics.append(
                    {"TopicName": res4[1], "TopicScore1": res4[2], "TopicScore2": res4[3], "Keywords": res4[4],"Length":lenght})
        r_topics2 = sorted(r_topics, key=lambda k: k['TopicScore1'], reverse=True)
        r_topics2 = r_topics2[:10]
        for topic in r_topics2:
            topic_writer.writerow([topic["TopicName"], topic["TopicScore1"], topic["TopicScore2"], topic["Keywords"], res[0], topic["Length"]])


    pro_file.close()
    pro_loc_file = open(output_path + "/project_locations.csv", 'wb')
    pro_loc_writer = csv.writer(pro_loc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    pro_loc_writer.writerow(["SIP_ID", "City", "Country", "Longitude", "Latitude"])
    for pro in projects:
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
            pro_loc_writer.writerow([res[0],city,country,res[3],res[4]])
    for act_id in actor_ids:
        sql = "SELECT idActors,ActorName,ActorWebsite FROM EDSI.Actors where idActors="+str(act_id)
        print act_id
        cursor.execute(sql)
        results = cursor.fetchall()
        for res in results:
            actor_writer.writerow([res[0],res[1].encode('utf-8'),res[2]])
    pro_loc_file.close()
    pro_act_file.close()
    actor_file.close()
    topic_file.close()


