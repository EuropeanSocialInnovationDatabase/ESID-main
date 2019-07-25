import os
from pymongo import MongoClient

import MySQLdb
from database_access import *

mongo_client = MongoClient()
mongo_db = mongo_client.ESID

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
if not os.path.exists("Kickstarter_additional"):
    os.mkdir("Kickstarter_additional")
sql = 'SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%Kick%") limit 100'

cursor.execute(sql)
results = cursor.fetchall()
projectList = []
text_array = []
classa = []
for res in results:
    projectId = res[5]
    SocialInnovation = res[6]

    des_sql = 'SELECT * FROM EDSI.AdditionalProjectData where FieldName like "%Desc%" and Projects_idProjects=' + str(
        projectId)
    cursor.execute(des_sql)
    results2 = cursor.fetchall()
    text = ""
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(projectId)},
                                                       no_cursor_timeout=True).batch_size(100)
    for res2 in results2:
        text = text + " " + res2[2]
    for doc in documents:
        text = text + " " + doc['translation']
    #new_text = text_cleaner.clean_text(text)
    if len(text) < 200:
        continue
    f = open("Kickstarter_additional/"+str(projectId)+".txt","w")
    f.write(text.encode("utf-8"))
    f.close()