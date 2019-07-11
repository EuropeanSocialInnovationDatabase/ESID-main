import MySQLdb
from database_access import *
import csv
import sys
import os

if __name__ == '__main__':
    Euro_County_list = ['Albania','Andora','Armenia','Austria','Azerbaijan','Belarus','Belgium','Bosnia and Herzegovina','Bulgaria',
                        'Croatia','Cyprus','Czech republic','Denmark','Estonia','Finland','France','Georgia','Germany','Greece',
                        'Hungary','Iceland','Ireland','Italy','Kazakhstan','Kosovo','Latvia','Liechtenstein','Lithuania','Luxembourg',
                        'Malta','Moldova','Monaco','Montenegro','Netherlands','North Macedonia','Norway','Poland','Portugal','Romania',
                        'Russia','San Marino','Serbia','Slovakia','Slovenia','Spain','Sweden','Switzerland','Turkey','Ukraine','UK',
                        'Vatican','Holy See','European Union']
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
        Outputs = 0
        Objective = 0
        Actors = 0
        Innovativeness = 0
        projects.append(res)
        id = res[0]
        sql = "SELECT Projects_idProjects,City,Country,Longitude,Latitude FROM EDSI.ProjectLocation where Projects_idProjects =" + str(
            id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for resS in results:
            if resS[1] == None:
                city = ""
            else:
                city = resS[1].encode('utf-8')
            if resS[2] == None:
                country = ""
            else:
                country = resS[2].encode('utf-8')
        if country not in Euro_County_list:
            continue
        if res[4] == None:
            web = ""
        else:
            web = res[4].encode('utf-8')
        ########################################################
        q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%Manual%' and Projects_idProjects={0}".format(
            res[0]);
        cursor.execute(q4)
        marks = cursor.fetchall()
        if len(marks) == 0:
            q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(
                res[0]);
            cursor.execute(q4)
            marks = cursor.fetchall()
        for mark in marks:
            Outputs = mark[1]
            Objective = mark[2]
            Actors = mark[3]
            Innovativeness = mark[4]
            if Outputs > 1:
                Outputs = 1
            if Objective >1:
                Objective = 1
            if Actors>1:
                Actors =1
            if Innovativeness > 1:
                Innovativeness = 1
        ########################################################

        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
            res[0])
        cursor.execute(q3)
        descriptions = cursor.fetchall()
        Descriptions = []
        for description in descriptions:
            Descriptions.append(description[2])
        if len(Descriptions) == 0:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
                res[0])

            cursor.execute(q3)
            descriptions = cursor.fetchall()

            for description in descriptions:
                Descriptions.append(description[2])
        if len(Descriptions) == 0:
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
                res[0])
            cursor.execute(q3)
            descriptions = cursor.fetchall()
            for descriptionA in descriptions:
                if descriptionA[2] == "":
                    continue
                Descriptions.append(descriptionA[2])
        if len(Descriptions)>0:
            description = Descriptions[0]
        else:
            description = ""
        pro_writer.writerow([res[0],res[1].encode('utf-8'),res[2],res[3],web,description.encode("utf-8"),Objective,Actors,Outputs,Innovativeness])

        sql3 = "SELECT Actors_idActors,Projects_idProjects,OrganisationRole FROM EDSI.Actors_has_Projects where Projects_idProjects="+str(res[0])
        cursor.execute(sql3)
        results3 = cursor.fetchall()
        for res3 in results3:
            actor_ids.append(res3[0])
            pro_act_writer.writerow(res3)
        q5 = "Select TopicName,TopicScore,TopicScore2,KeyWords,Text_length from Project_Topics where Projects_idProject={0} and (Version like '%v4%' or Version like '%Manual%') and Exclude=0 order by TopicScore desc limit 10".format(
            str(res[0]));
        cursor.execute(q5)
        results4 = cursor.fetchall()
        r_topics = []
        for res4 in results4:
            if res4[1] > 0.7:
                lenght = res4[4]
                r_topics.append( {"TopicName": res4[0], "TopicScore1": res4[1], "TopicScore2": res4[2], "Keywords": res4[3],"Length":lenght})

        # sql4 = "Select * from EDSI.Project_Topics where (Version like '%v4%' or Version like '%Manual%') and Projects_idProject ="+str(res[0])
        # cursor.execute(sql4)
        # results4 = cursor.fetchall()
        # r_topics = []
        # for res4 in results4:
        #     lenght = res4[9]
        #     score = res4[2]
        #     if lenght > 100000:
        #         score = score * 10
        #     elif lenght > 50000:
        #         score = score * 7
        #     elif lenght > 30000:
        #         score = score * 2
        #     elif lenght > 10000:
        #         score = score * 1.7
        #     if score > 3:
        #         r_topics.append(
        #             {"TopicName": res4[1], "TopicScore1": res4[2], "TopicScore2": res4[3], "Keywords": res4[4],"Length":lenght})
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


