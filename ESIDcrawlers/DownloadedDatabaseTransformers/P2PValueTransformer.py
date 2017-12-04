from database_access import *
import MySQLdb
import sys
import csv
import datetime

class Project:
    def __init__(self):
        self.database_id = -1
        self.project_name = ""
        self.description = ""
        self.homepage = ""  # Location.City
        self.facebook = ""
        self.twitter = ""
        self.email = ""
        self.organisation_type = ""
        self.physical_address = ""
        self.organisation_type2 = ""
        self.start_date = ""
        self.platform_lang = ""
        self.phone = ""
        self.keywords = []
        self.activity_type = ""
        self.scope = ""


if __name__ == '__main__':
    print("Starting SIMPACTTransformer")
    if(len(sys.argv)<2):
        print "This scripts needs one arguments: csv with projects"
        exit(1)
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    organisations_arg = sys.argv[1]
    projects = []
    with open(organisations_arg, 'rb') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in orgreader:
            if(i==0):
                i+=1
                continue
            pro = Project()
            pro.project_name = row[0]
            pro.description = row[1]
            pro.homepage = row[2]
            social_media = row[3].split(",")
            for s in social_media:
                if "facebook.com" in s:
                    pro.facebook = s
                if "twitter.com" in s:
                    pro.twitter = s
            pro.email = row[4]
            pro.organisation_type = row[6]
            pro.physical_address = row[7]
            pro.organisation_type2 = row[8]
            pro.start_date = row[9].split("-")[0]+"-01-01"

            pro.platform_lang = row[10]
            pro.phone = row[11]
            pro.keywords = row[12].split(",")
            pro.activity_type = row[13]
            pro.scope = row[18]
            projects.append(pro)
            i+=1
    for project in projects:
        print "Saving "+project.project_name
        if project.start_date != "-01-01":
            sql_org = "Insert into Projects (ProjectName,Type,ProjectWebpage,FacebookPage,ProjectTwitter,FirstDataSource,DataSources_idDataSources,DateStart) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')"
            cursor.execute(sql_org.format(project.project_name, project.organisation_type+"; "+project.organisation_type2,project.homepage,project.facebook,project.twitter,
                                     'P2P Value directory',16,project.start_date))
        else:
            sql_org = "Insert into Projects (ProjectName,Type,ProjectWebpage,FacebookPage,ProjectTwitter,FirstDataSource,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')"
            cursor.execute(
                sql_org.format(project.project_name, project.organisation_type + "; " + project.organisation_type2,
                               project.homepage, project.facebook, project.twitter,
                               'P2P Value directory', 16, project.start_date))
        org_id_inTable = cursor.lastrowid
        project.database_id = org_id_inTable
        db.commit()
        #
        sql_loc = "Insert into ProjectLocation (Type,Address,PhoneContact,EmailContact,Projects_idProjects) VALUES " \
                      "(%s,%s,%s,%s,%s)"
        cursor.execute(sql_loc, ("Main", project.physical_address,project.phone,project.email,
                                     project.database_id))
        db.commit()
        #
        sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
        "Description", project.description, project.database_id, "http://directory.p2pvalue.eu/download/all-cbpp?eid=1554&return-url=download"))
        db.commit()

        sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
            "platform_lang", project.platform_lang, project.database_id,
            "http://directory.p2pvalue.eu/download/all-cbpp?eid=1554&return-url=download"))
        db.commit()

        sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
            "activity_type", project.activity_type, project.database_id,
            "http://directory.p2pvalue.eu/download/all-cbpp?eid=1554&return-url=download"))
        db.commit()

        sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        cursor.execute(sql_short_desc, (
            "Scope", project.scope, project.database_id,
            "http://directory.p2pvalue.eu/download/all-cbpp?eid=1554&return-url=download"))
        db.commit()
        for keyword in project.keywords:
            sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_short_desc, (
                "Keyword", keyword, project.database_id,
                "http://directory.p2pvalue.eu/download/all-cbpp?eid=1554&return-url=download"))
            db.commit()

    print "Done!!!!"
