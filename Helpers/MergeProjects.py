import MySQLdb
from database_access import *
dba = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = dba.cursor()

MainProject = "13214"
ProjectsToMerge = ["2303","13320"]
def checkNone(string):
    if string == None:
        string = 'Null'
    return string

for pro in ProjectsToMerge:
    sql = "Update Projects set Exclude=1 where idProjects={0}".format(pro)
    cursor.execute(sql)
    sql2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro)
    cursor.execute(sql2)
    results = cursor.fetchall()
    locs_to_merge = []
    locs_main = []
    for res in results:
        loc = {}
        loc['id']=res[15]
        loc['Type']=checkNone(res[1])
        loc['Address'] = checkNone(res[3])
        loc['City'] = checkNone(res[4])
        loc['Country'] = checkNone(res[5])
        loc['PostCode'] = checkNone(res[6])
        loc['PhoneContact'] = checkNone(res[7])
        loc['EmailContact'] = checkNone(res[8])
        loc['Longitude'] = checkNone(res[9])
        loc['Latitude'] = checkNone(res[10])
        locs_to_merge.append(loc)

    sql3 = "Select * from ProjectLocation where Projects_idProjects={0}".format(MainProject)
    cursor.execute(sql3)
    results = cursor.fetchall()
    for res in results:
        loc = {}
        loc['id']=res[15]
        loc['Type']=checkNone(res[1])
        loc['Address'] = checkNone(res[3])
        loc['City'] = checkNone(res[4])
        loc['Country'] = checkNone(res[5])
        loc['PostCode'] = checkNone(res[6])
        loc['PhoneContact'] = checkNone(res[7])
        loc['EmailContact'] = checkNone(res[8])
        loc['Longitude'] = checkNone(res[9])
        loc['Latitude'] = checkNone(res[10])
        locs_main.append(loc)

    for l in locs_to_merge:
        contains_City = False
        contains_Country = False
        for l2 in locs_main:
            if l["City"]==l2["City"]:
                contains_City = True
            if l["Country"] == l2["Country"]:
                contains_Country = True
        if contains_City:
            continue
        if contains_Country:
            sql3 = "Update ProjectLocation set City='{0}' where Country='{1}' and Projects_idProjects='{2}'".format(l["City"],l["Country"],MainProject)
            cursor.execute(sql3)
            dba.commit()
            continue
        sql4 = "Insert into ProjectLocation (Type,Address,City,Country,PostCode,PhoneContact,EmailContact,Longitude,Latitude,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',{7},{8},{9},{10})".format(l["Type"],l["Address"],l["City"],l["Country"],l["PostCode"],l["PhoneContact"],l["EmailContact"],l["Longitude"],l["Latitude"],MainProject,l["id"])
        cursor.execute(sql4)
        dba.commit()
    sql5 = "SELECT * FROM AdditionalProjectData where Projects_idProjects = {0}".format(pro)
    cursor.execute(sql5)
    results = cursor.fetchall()
    for res in results:
        sql6 = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) Values ('{0}',\"{1}\",'{2}','{3}','{4}')".format(res[1],res[2].replace("\"","'").encode('utf-8'),MainProject,res[4],res[5])
        cursor.execute(sql6)
        dba.commit()
    dba.commit()
    sql6 = "SELECT * FROM Actors_has_Projects where Projects_idProjects = {0}".format(pro)
    cursor.execute(sql6)
    results = cursor.fetchall()
    for res in results:
        try:
            sql7 = "Insert into Actors_has_Projects (Actors_idActors,Projects_idProjects,OrganisationRole) Values ('{0}','{1}','{2}')".format(res[0],MainProject,res[2])
            cursor.execute(sql7)
            dba.commit()
        except:
            print("already exist ")
    print("Done "+pro)
print "Done all"


