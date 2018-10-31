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
    pro_writer.writerow(["SIP_ID","Title","ObjectiveScoreM1","ActorScoreM1","OutputScoreM1","InnovativenessScoreM1",
                         "ObjectiveScoreM2", "ActorScoreM2", "OutputScoreM2", "InnovativenessScoreM2"])
    for res in results:
        projects.append(res)
        sql11 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects="+str(res[0])
        cursor.execute(sql11)
        Objective1 = 0
        Actors1 = 0
        Outputs1 = 0
        Innovativeness1 = 0
        results11 = cursor.fetchall()
        for res11 in results11:
            Objective1 = res11[2]
            Actors1 = res11[3]
            Outputs1 = res11[1]
            Innovativeness1 = res11[4]
        sql11 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v12%' and Projects_idProjects=" + str(
            res[0])
        cursor.execute(sql11)
        Objective2 = 0
        Actors2 = 0
        Outputs2 = 0
        Innovativeness2 = 0
        results22 = cursor.fetchall()
        for res22 in results22:
            Objective2 = res22[2]
            Actors2 = res22[3]
            Outputs2 = res22[1]
            Innovativeness2 = res22[4]
        pro_writer.writerow(
        [res[0], res[1].encode('utf-8'), Objective1, Actors1, Outputs1,
         Innovativeness1,Objective2, Actors2, Outputs2,
         Innovativeness2])
