# -*- coding: utf-8 -*-
import MySQLdb
from database_access import *
import requests
import json
project_text = """
A social financial system where inflation is transformed into basic income using blockchain.

We believe that basic income is inevitable because of the growing optimisation and automation in almost every sector of our society, which probably will lead to loss of numerous jobs. The programmable nature of blockchain technology is making it possible to introduce a fair way to create a basic income. The idea is to issue a blockchain-based token (cryptocurrency) programmed with a negative interest in currency board with a fiat currency 1:1. The fairness is in the financing of the basic income, which will come not from the societal consumption, but from the storage of means.


"""
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql_projects = "Select ProjectName, idProjects from Projects where Exclude = 0"
cursor.execute(sql_projects)
results = cursor.fetchall()

for pro in results:
    name = pro[0]
    id = pro[1]
    sql_desc = "Select FieldName,Value from AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(id)
    cursor.execute(sql_desc)
    descriptions = cursor.fetchall()
    Descrip= ""
    for desc in descriptions:
        Descrip = Descrip +" " +desc[1]
    project_text = name+ "    "+Descrip

    r = requests.post("http://services.gate.ac.uk/knowmak/classifier/project", data=project_text.encode('ascii','ignore'))
    print(r.status_code, r.reason)
    data = json.loads(r.text)
    for clas in data["classification"]:
        keywords = ""
        for key in data["classification"][clas]["keywords"]:
            keywords = keywords+","+key
        keywords = keywords[1:]
        insert_sql = "Insert into Project_Topics (TopicName,TopicScore,KeyWords,Projects_idProject,Comment,Version,Sources,TopicScore2)" \
                     "VALUES ('{0}',{1},'{2}',{3},'{4}','{5}','{6}',{7})".format(clas,data["classification"][clas]["score"][0],
                                                                             keywords,id,"First data, concatinated descriptions only with titles","06/11/2018 v1 SI","Title,Desctiptions",data["classification"][clas]["score"][1])
        cursor.execute(insert_sql)
        db.commit()
    # print(r.text)
    # data = json.loads(r.text)
    # for clas in data["classification"]:
    #     print("Class:" + clas + ":" + str(data["classification"][clas]["score"]))
    #     print "Keywords"
    #     for key in data["classification"][clas]["keywords"]:
    #         print key + ":" + str(data["classification"][clas]["keywords"][key])