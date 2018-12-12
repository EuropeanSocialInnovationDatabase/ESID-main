import os
import MySQLdb
from database_access import *

directory = "Descriptions"
if not os.path.exists(directory):
    os.makedirs(directory)

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
query_projects = "Select idProjects from Projects where Exclude=0"
cursor.execute(query_projects)
results = cursor.fetchall()
for r in results:
    idProject = r[0]
    query2 = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(idProject)
    cursor.execute(query2)
    project_text = ""
    res2 = cursor.fetchall()
    for r2 in res2:
        if "Short" in r2[1]:
            continue
        else:
            project_text = project_text+" "+r2[2]
    if project_text=="" or project_text==" ":
        continue
    f = open(directory+"/"+str(idProject)+".txt", "w")
    f.write(project_text.encode('utf-8'))
    f.close()