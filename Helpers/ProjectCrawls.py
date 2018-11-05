import MySQLdb
from database_access import *

from pymongo import MongoClient

client = MongoClient()
db_M = client.ESID
everything = db_M.crawl20180801_translated.find({})
db = MySQLdb.connect(host, username, password, database, charset='utf8mb4')
cursor = db.cursor()
for doc in everything:
    text = doc['translation'].replace("'"," ").replace('"',' ').encode('utf-8').decode('utf-8').encode('utf-8')
    text = text
    project_id = doc['mysql_databaseID']
    sql = "Insert into ProjectCrawls (Projects_idProjects,CrawledText) VALUES ({0},'{1}')".format(project_id,text)
    cursor.execute(sql)
    db.commit()
    print(project_id)
print("Done")
