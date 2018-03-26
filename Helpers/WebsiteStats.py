import MySQLdb
import requests
from database_access import *
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql_projects = "Select ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,idProjects from Projects where Exclude = 0"

cursor.execute(sql_projects)
results = cursor.fetchall()
number_of_missing_sites = 0
number_of_inactive_sites = 0
number_of_active_sites = 0
for result in results:
    site = result[1]

    project_id = result[4]
    if site == None:
        number_of_missing_sites = number_of_missing_sites + 1
        continue
    print "Processing "+str(site.encode('utf-8').strip())
    if site == "":
        number_of_missing_sites = number_of_missing_sites +1
        continue
    if "http" not in site:
        site = "http://"+site
    try:
        r = requests.get(site)
        if r.status_code == 200:
            number_of_active_sites = number_of_active_sites + 1
        else:
            number_of_inactive_sites = number_of_inactive_sites + 1

            cursor.execute("Update Projects SET InactiveWebsite = 1 where idProjects=%s",(project_id,))
            db.commit()
    except:
        number_of_inactive_sites = number_of_inactive_sites + 1
        print "Exception happened"
        cursor.execute("Update Projects SET InactiveWebsite = 1 where idProjects=%s", (project_id,))
        db.commit()

print("Number of active websites: "+str(number_of_active_sites) )
print("Number of inactive websites: "+str(number_of_inactive_sites) )
print("Number of missing websites: "+str(number_of_missing_sites) )
