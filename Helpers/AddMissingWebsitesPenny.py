#MissingWebsitesESID_Task_1_Penny_edits.csv
import MySQLdb
import csv

from database_access import *
print("aaa")
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
csvfile =  open('MissingWebsitesESID_Task_1_Penny_UPDATED_edit_31.07.2018.csv', 'rb')
csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
for row in csvreader:
    penny =  row[3]
    id = row[0]
    print str(id) + "  "+ str(penny)
    if "http" in penny:
        sql = "Update Projects set ProjectWebpage='{0}', HadMissingWebpage=2 where idProjects={1} and HadMissingWebpage=2".format(penny,id)
        cursor.execute(sql)
        db.commit()
