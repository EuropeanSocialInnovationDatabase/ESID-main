import os
import csv
import MySQLdb
from pymongo import MongoClient
from database_access import *
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
directory = "paper_output_files"
if not os.path.exists(directory):
    os.makedirs(directory)

file_in = "../TextMining/Classifiers/DatabaseWithKickStarter/preds_innovativeness.csv"
file_out = directory + "/preds_innovativeness.csv"
file1 = open(file_out,'w')
writer = csv.writer(file1)
writer.writerow(["idproject","prediction","actual", "society", "health", "security", "city","country", "text_len","language","excluded"])
with open(file_in, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
        project_id = row[0]
        print("working on" + str(project_id))
        prediction = row[1]
        actual = row[2]
        cursor.execute(
            "SELECT * FROM EDSI.Projects where idProjects=" + project_id)
        results = cursor.fetchall()
        excluded = 0
        for res in results:
            if res[19] == 1:
                excluded = 1
        cursor.execute("SELECT * FROM EDSI.Project_Topics where TopicScore>0.8 and Version like '%v5%' and Projects_idProject="+project_id)
        results = cursor.fetchall()
        society = 0
        health = 0
        security = 0
        for res in results:
            if "society" in res[1] or "co_creation" in res[1] or "cultural_heritage" in res[1] or "democracy" in res[1] or "http://www.gate.ac.uk/ns/ontologies/knowmak/education" == res[1] or "employment" in res[1] or "entrepreneurship" in res[1] or "global_engagement" in res[1] or "housing" in res[1] or "knowledge_transfer" in res[1] or "local_engagement" in res[1] or "migration" in res[1] or "poverty" in res[1] or "social_inequality" in res[1]:
                society = 1
            if "health" in res[1] or "active_ageing_and_self_management_of_health" in res[1] or "preventing_disease" in res[1] or "treating_and_managing_disease" in res[1] or "e_health" in res[1] or "health_biotechnology" in res[1] or "health_care_provision_and_integrated_care" or res[1] or "health_data" in res[1] or "personalized_medicine" in res[1] or "pharmaceuticals" in res[1] or "social_care" in res[1]:
                health = 1
            if "security" in res[1] or "catastrophe_fighting" in res[1] or "crime_and_terrorism" in res[1]:
                security = 1
        cursor.execute(
            "SELECT * FROM EDSI.ProjectLocation where Projects_idProjects=" + project_id)
        results = cursor.fetchall()
        city = ""
        country = ""
        for res in results:
            city = res[4]
            country = res[5]
            break
        des_sql = 'SELECT * FROM EDSI.AdditionalProjectData where FieldName like "%Desc%" and Projects_idProjects=' + str(
            project_id)
        cursor.execute(des_sql)
        results2 = cursor.fetchall()
        language = ""
        text = ""
        documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                           no_cursor_timeout=True).batch_size(100)
        for res2 in results2:
            text = text + " " + res2[2]
        for doc in documents:
            text = text + " " + doc['translation']
            language = doc["Language"]
        text_len = len(text)
        if city != None:
            city = city.encode('utf-8')
        writer.writerow([project_id,prediction,actual,society,health,security,city,country,text_len,language,excluded])
file1.close()
print("Done all")





