import MySQLdb
import requests
from database_access import *
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where Exclude = 0 and InactiveWebsite=1"
cursor.execute(sql_projects)
results = cursor.fetchall()
number_of_available = 0
number_of_unnavailable = 0
for result in results:
    site = result[1]
    project_id = result[4]
    try:
        r = requests.get("http://archive.org/wayback/available?url="+site)
        if r.status_code == 200:
            json_ret = r.json()
            print json_ret
            if json_ret['archived_snapshots'] == {}:
                number_of_unnavailable = number_of_unnavailable + 1
                print "Unavailable"
            else:
                number_of_available = number_of_available + 1
        else:
            number_of_unnavailable = number_of_unnavailable + 1
            print "Unavailable"
    except:
        number_of_unnavailable = number_of_unnavailable + 1
        print "Unavailable"

print("Number of available websites: "+str(number_of_available))
print("Number of unavailable websites: "+str(number_of_unnavailable))

