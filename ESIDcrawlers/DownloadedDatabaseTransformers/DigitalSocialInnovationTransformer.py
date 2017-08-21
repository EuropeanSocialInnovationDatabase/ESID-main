#!/usr/bin/env python
# -*- coding: utf-8 -*-

from my_settings import *
import MySQLdb
import sys
import csv

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


if __name__ == '__main__':
    print("Starting DigitalSocialInnovationTransformer")
    if(len(sys.argv)<3):
        print "This scripts needs two arguments: csv with organisations and csv with projects"
        exit(1)
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
 #TODO: Save data to database

