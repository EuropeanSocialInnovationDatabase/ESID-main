#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database_access import *
import MySQLdb
import sys
import csv
import datetime

class Organisation:
    def __init__(self):
        self.organisation_id = ""
        self.database_id = -1
        self.organisation_name = "" # ActorName
        self.website = "" #ActorWebsite
        self.short_description = "" # ActorsAdditionalData-ActorShortDescription
        self.long_description = ""# ActorsAdditionalData-ActorLongDescription
        self.country ="" # Location.Country
        self.region = "" #Location.City
        self.latitude = -1 #Location.Latitude
        self.longitude = -1#Location.Longitude
        self.address = ""#Location.address
        self.organisation_type = ""#Actor.Type
        self.organisation_size= ""#Size
        self.start_date = ""#StartDate
        self.linked_project_ids = [] # Actors_has_projects
        self.tags = [] # ActorsAdditionalData
        self.network_tags = [] #ActorsAdditionalData
        self.facebook = None # ActorFacebookPage


class Project:
    def __init__(self):
        self.project_id = ""
        self.database_id = -1
        self.project_name = "" # ProjectName
        self.website = "" # ProjectWebpage
        self.short_description = "" # AdditionalProjectData
        self.long_description = "" # AdditionalProjectData
        self.social_impact = "" #OutreachImpact
        self.start_date = "" #DateStart
        self.end_date = "" #DateEnd
        self.country = "" # ProjectLocation
        self.region = "" # City
        self.latitude = -1 #Longitude
        self.longitude = -1 # Latitude
        self.linked_organisation_ids = [] #Actor_has_Projects
        self.who_we_help_tags = [] #AdditionalProjectData.WhoWeHelp
        self.support_tags = [] # AdditionalProjectData.SupportTags
        self.focus = [] # AdditionalProjectData.Focus
        self.technology = [] # AdditionalProjectData.Technology
        self.facebook = None


if __name__ == '__main__':
    print("Starting DigitalSocialInnovationTransformer")
    projects_added = 0
    projects_excluded = 0
    if(len(sys.argv)<2):
        print "This scripts needs one arguments: csv with projects"
        exit(1)
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    projects_arg = sys.argv[1]
    projects = []
    with open(projects_arg, 'rb') as csvfile:
        proreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in proreader:
            if (i == 0):
                i += 1
                continue
            pro = Project()
            pro.project_id = row[0]
            pro.project_name = row[1]
            pro.website = row[2]
            pro.short_description = row[3]
            pro.long_description = row[4]
            pro.social_impact = row[5]
            pro.start_date = row[6]
            pro.end_date = row[7]
            pro.country = row[8]
            pro.region = row[9]
            pro.latitude = row[10]
            pro.longitude = row[11]
            pro.linked_organisation_ids = row[12].replace('"','').split(',')
            pro.who_we_help_tags = row[13].replace('"','').split(',')
            pro.support_tags = row[14].replace('"','').split(',')
            pro.focus = row[15].replace('"','').split(',')
            pro.technology = row[16].replace('"','').split(',')
            projects.append(pro)
            i += 1
    for project in projects:
        if "facebook.com" in project.website:
            project.facebook = project.website
            project.website = None
        if project.start_date=="":
            project.start_date = None
        if project.end_date=="":
            project.end_date = None
        d1 = datetime.datetime.now().date()
        if project.longitude=="":
            project.longitude = None
        if project.latitude =="":
            project.latitude = None
    projects_in_DB = []
    sql_check = "SELECT * from Projects where FirstDataSource = 'Digital Social Innovation Database'"
    cursor.execute(sql_check)
    results = cursor.fetchall()

    for row in results:
        projects_in_DB.append(row[2])
    # for project in projects:
    #     if project.project_name not in projects_in_DB:
    #         print "Adding a project: "+project.project_name
    #         projects_added = projects_added + 1
    #         sql_pro = "Insert into Projects (ProjectName,DateStart,DateEnd, Ongoing," \
    #                   "ProjectWebpage,FacebookPage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    #         cursor.execute(sql_pro, (project.project_name,
    #                                  project.start_date, project.end_date, "1", project.website, project.facebook,
    #                                  'Digital Social Innovation Database',
    #                                  '1'))
    #         pro_id_inTable = cursor.lastrowid
    #         project.database_id = pro_id_inTable
    #         db.commit()
    #         sql_proloc = "Insert into ProjectLocation(Type,City,Country,Longitude,Latitude,Projects_idProjects) VALUES('Main',%s,%s,%s,%s,%s)"
    #         cursor.execute(sql_proloc,
    #                        (project.region, project.country, project.longitude, project.latitude, project.database_id))
    #
    #         sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                          "VALUES(%s,%s,%s,NOW(),%s)"
    #         cursor.execute(sql_short_desc, (
    #         "Short Description", project.short_description, project.database_id, "https://digitalsocial.eu"))
    #         db.commit()
    #
    #         sql_long_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                         "VALUES(%s,%s,%s,NOW(),%s)"
    #         cursor.execute(sql_long_desc, (
    #             "Long Description", project.long_description, project.database_id, "https://digitalsocial.eu"))
    #         db.commit()
    #
    #         sql_soc_imp = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                       "VALUES(%s,%s,%s,NOW(),%s)"
    #         cursor.execute(sql_soc_imp, (
    #             "Social Impact", project.long_description, project.database_id, "https://digitalsocial.eu"))
    #         db.commit()
    #         sql_soc_imp2 = "Insert into OutreachImpact (Type,Name,Description,URL,Projects_idProjects)" \
    #                        "VALUES(%s,%s,%s,%s,%s)"
    #         cursor.execute(sql_soc_imp2, (
    #             "Social Impact", "", project.social_impact, "https://digitalsocial.eu", project.database_id))
    #         db.commit()
    #
    #         for tag in project.support_tags:
    #             sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                            "VALUES(%s,%s,%s,NOW(),%s)"
    #             cursor.execute(sql_tag_desc, (
    #                 "Support Tag", tag, project.database_id,
    #                 "https://digitalsocial.eu"))
    #             db.commit()
    #         for tag in project.technology:
    #             sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                            "VALUES(%s,%s,%s,NOW(),%s)"
    #             cursor.execute(sql_tag_desc, (
    #                 "Technology", tag, project.database_id,
    #                 "https://digitalsocial.eu"))
    #             db.commit()
    #         for tag in project.focus:
    #             sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                            "VALUES(%s,%s,%s,NOW(),%s)"
    #             cursor.execute(sql_tag_desc, (
    #                 "Focus", tag, project.database_id,
    #                 "https://digitalsocial.eu"))
    #             db.commit()
    #         for tag in project.focus:
    #             sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
    #                            "VALUES(%s,%s,%s,NOW(),%s)"
    #             cursor.execute(sql_tag_desc, (
    #                 "Who we help", tag, project.database_id,
    #                 "https://digitalsocial.eu"))
    #             db.commit()
    for project_db in projects_in_DB:
        existsInCSV = False
        for proj_csv in projects:
            if proj_csv.project_name == str(project_db.encode('ascii','ignore')):
                existsInCSV = True
        if existsInCSV == False:
            print "Removing project:"+project_db
            projects_excluded = projects_excluded + 1
            cursor.execute("Update Projects set Exclude = 1 where ProjectName=%s",(project_db,))
            db.commit()
    print "Completed!"
    print "Project added:"+str(projects_added)
    print "Project excluded:" + str(projects_excluded)


