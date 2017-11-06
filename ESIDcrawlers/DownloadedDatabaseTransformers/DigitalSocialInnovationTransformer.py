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
    if(len(sys.argv)<3):
        print "This scripts needs two arguments: csv with organisations and csv with projects"
        exit(1)
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    organisations_arg = sys.argv[1]
    projects_arg = sys.argv[2]
    organisations = []
    with open(organisations_arg, 'rb') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in orgreader:
            if(i==0):
                i+=1
                continue
            org = Organisation()
            org.organisation_id = row[0]
            org.organisation_name = row[1]
            org.website = row[2]
            org.short_description = row[3]
            org.long_description = row[4]
            org.country = row[5]
            org.region = row[6]
            org.latitude=row[7]
            org.longitude = row[8]
            org.address = row[9]
            org.organisation_type = row[10]
            org.organisation_size = row[11]
            org.start_date = row[12]
            org.linked_project_ids = row[13].replace('"','').split(',')
            org.tags = row[14].replace('"','').split(',')
            org.network_tags = row[15].replace('"','').split(',')
            organisations.append(org)
            i+=1
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
    for organisation in organisations:
        # Academia/Research organisation -> Higher edicational institution
        # For-profit business -> Private for-profit business
        # Govrnment/Public Sector -> Public sector
        # Grassroots organisation or community network -> Grassroot/Community network
        # Social enterprise, charity, foundation or other non-profit -> Non-profit or Social Enterprise
        if (organisation.organisation_type == "Academia/Research organisation"):
            organisation.organisation_type = "Academia/Research organisation"
        if (organisation.organisation_type == "For-profit business"):
            organisation.organisation_type = "Private for-profit business"
        if (organisation.organisation_type == "Govrnment/Public Sector"):
            organisation.organisation_type = "Public sector"
        if (organisation.organisation_type == "Grassroots organisation or community network"):
            organisation.organisation_type = "Grassroot/Community network"
        if (organisation.organisation_type == "Social enterprise, charity, foundation or other non-profit"):
            organisation.organisation_type = "Non-profit or Social Enterprise"
        if organisation.start_date=="":
            organisation.start_date = None
        if organisation.organisation_size=="":
            organisation.organisation_size = None
        if organisation.website == "":
            organisation.website = None
        if (organisation.website is not None) and ("facebook.com" in organisation.website):
            organisation.facebook = organisation.website
            organisation.website = None
        if organisation.longitude=="":
            organisation.longitude = None
        if organisation.latitude =="":
            organisation.latitude = None
        insertActor = True
        try:
            sql_check = "SELECT * from Actors where ActorName like '%s'" % organisation.organisation_name
            cursor.execute(sql_check)
            results = cursor.fetchall()
            for row in results:
                insertActor = False
        except:
            insertActor = False
        if insertActor:
            sql_org = "Insert into Actors (ActorName,Type,SubType,Size,SourceOriginallyObtained,ActorWebsite,StartDate," \
                      "DataSources_idDataSources,ActorFacebookPage) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_org,(organisation.organisation_name,'S',organisation.organisation_type,
                                    organisation.organisation_size,'Digital Social Innovation Database',
                                    organisation.website,organisation.start_date,1,organisation.facebook))
            org_id_inTable = cursor.lastrowid
            organisation.database_id = org_id_inTable
            db.commit()
            try:
                sql_loc = "Insert into Location (Type,Address,City,Country,Longitude,Latitude,Actors_idActors) VALUES " \
                      "(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql_loc,("Headquarters",organisation.address,organisation.region,organisation.country,
                                    organisation.longitude,organisation.latitude,organisation.database_id))
            except:
                print organisation.longitude
            db.commit()

            sql_short_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_short_desc,("Short Description",organisation.short_description,organisation.database_id,"https://digitalsocial.eu"))
            db.commit()
            sql_long_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_long_desc, (
            "Long Description", organisation.long_description, organisation.database_id, "https://digitalsocial.eu"))
            db.commit()


            for tag in organisation.tags:
                sql_tag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                                "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_tag_desc, (
                    "Tag", tag, organisation.database_id,
                    "https://digitalsocial.eu"))
                db.commit()
            for tag in organisation.network_tags:
                sql_ntag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                                "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_ntag_desc, (
                    "Network Tag", tag, organisation.database_id,
                    "https://digitalsocial.eu"))
                db.commit()
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

        ongoing = 0
        if project.end_date is not None:
            if '/'in project.end_date:
                d2 = datetime.datetime.strptime(project.end_date, "%d/%m/%Y").date()
            else:
                d2 = datetime.datetime.strptime(project.end_date, "%Y-%m-%d").date()
            if d2 > d1:
                ongoing = 1
        insertProject = True
        try:
            sql_check = "SELECT * from Projects where ProjectName like '%s'" % project.project_name
            cursor.execute(sql_check)
            results = cursor.fetchall()

            for row in results:
                insertProject = False
        except:
            insertProject = False
        if insertProject:
            print "Inserting project: "+project.project_name
            sql_pro = "Insert into Projects (ProjectName,DateStart,DateEnd, Ongoing," \
                      "ProjectWebpage,FacebookPage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_pro, (project.project_name,
                                     project.start_date,project.end_date,ongoing,project.website,project.facebook,'Digital Social Innovation Database',
                                     '1'))
            pro_id_inTable = cursor.lastrowid
            project.database_id = pro_id_inTable
            db.commit()
            sql_proloc = "Insert into ProjectLocation(Type,City,Country,Longitude,Latitude,Projects_idProjects) VALUES('Main',%s,%s,%s,%s,%s)"
            cursor.execute(sql_proloc,(project.region,project.country,project.longitude,project.latitude,project.database_id))

            sql_short_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_short_desc,("Short Description",project.short_description,project.database_id,"https://digitalsocial.eu"))
            db.commit()

            sql_long_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_long_desc, (
            "Long Description", project.long_description, project.database_id, "https://digitalsocial.eu"))
            db.commit()

            sql_soc_imp = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                            "VALUES(%s,%s,%s,NOW(),%s)"
            cursor.execute(sql_soc_imp, (
                "Social Impact", project.long_description, project.database_id, "https://digitalsocial.eu"))
            db.commit()
            sql_soc_imp2 = "Insert into OutreachImpact (Type,Name,Description,URL,Projects_idProjects)" \
                          "VALUES(%s,%s,%s,%s,%s)"
            cursor.execute(sql_soc_imp2, (
                "Social Impact", "", project.social_impact, "https://digitalsocial.eu",project.database_id))
            db.commit()

            for tag in project.support_tags:
                sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_tag_desc, (
                    "Support Tag", tag, project.database_id,
                    "https://digitalsocial.eu"))
                db.commit()
            for tag in project.technology:
                sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                   "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_tag_desc, (
                        "Technology", tag, project.database_id,
                        "https://digitalsocial.eu"))
                db.commit()
            for tag in project.focus:
                sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                   "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_tag_desc, (
                        "Focus", tag, project.database_id,
                        "https://digitalsocial.eu"))
                db.commit()
            for tag in project.focus:
                sql_tag_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                   "VALUES(%s,%s,%s,NOW(),%s)"
                cursor.execute(sql_tag_desc, (
                        "Who we help", tag, project.database_id,
                        "https://digitalsocial.eu"))
                db.commit()
            for link_org_id in project.linked_organisation_ids:
                for organisation in organisations:
                    if organisation.organisation_id == link_org_id:
                        sql_org_pro = "Insert into Actors_has_Projects(Actors_idActors,Projects_idProjects,OrganisationRole) Values" \
                              "(%s,%s,%s)"
                        try:
                            cursor.execute(sql_org_pro,(organisation.database_id,project.database_id,""))
                            db.commit()
                        except:
                            pass
    print "Completed!"

