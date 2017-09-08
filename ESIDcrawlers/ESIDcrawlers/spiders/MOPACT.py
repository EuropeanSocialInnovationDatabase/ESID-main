#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from HTMLParser import HTMLParser
import MySQLdb
from database_access import *
import re

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class InnovageSpider(scrapy.Spider):
    name = "MOPACT"
    num = 0

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = ["http://mopact.group.shef.ac.uk/research-posts/innovations-8/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations-6/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations-3/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations-4/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations-5/",
                "http://mopact.group.shef.ac.uk/research-posts/innovations-7/"]

        # for i in range(0,32):
        #     urls.append("http://www.innovage.group.shef.ac.uk/innovation-database.html?page="+str(i))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        source_page = response.url
        body = response.body.strip().replace("  "," ")
        #regex = '(<strong>|<b>)([A-Za-z0-9&#!;: ()-]*)(</strong>|</b>)</p>[\n ]*<p>([a-zA-Z0-9<> ="/\n]*)(<strong>|<b>)([a-zA-Z0-9<>&;, ="/\n]*)(</strong>|</b>)</p>[\n ]+<p><strong>([A-Za-z :]+)</strong></p>[\n ]*<ul>([A-Za-z0-9<>()\n,. &;/-]*)</ul>[\n ]*<p>([A-Za-z0-9\xA0 ,.\ö€£$(\)%</>\n&#;:-]*)</p>[\n ]<p>([<a-z0-9A-Z%_?&; =":/.>\n-]*)</p>'
        #m = re.findall(regex,body)
        projects = body.split('<hr />')

        projects = projects[1].split("Return to top")
        new_projects = []
        for project in projects:
            if "<br />" in project:
                project2 = project.split("<br />")
                for pro in project2:
                    pattern = '(<strong>|<b>)([A-Za-z0-9&#!;: ()-]*)(</strong>|</b>)'
                    m = re.findall(pattern, pro)
                    if len(m)>0 and len(m)<4:
                        project2=[]
                        project2.append(project)
                for pro in project2:
                    if len(pro)>100:
                        new_projects.append(pro)
            else:
                new_projects.append(project)
        new_projects.remove(new_projects[len(new_projects)-1])
        #print "AAAA"
        project_country = ""
        for project in new_projects:
            regex = '(<strong>|<b>)([A-Za-z0-9&#!;: ()-]*)(</strong>|</b>)'
            m = re.findall(regex, project)
            if m!=None:
                project_name = ""
                for item in m:
                    if project_name == "":
                        project_name = item[1]
                        print project_name
                    if(item[1]!="AAI Domains:" and project_name is not item[1] and item[1]!="Websites:"and item[1]!="Website:"):
                        project_country = item[1]
                    #print item
            regex = '<ul>([A-Za-z0-9<>()\n,. &;/-]*)</ul>'
            m = re.findall(regex, project)
            if m!=None:
                for item in m:
                    project_areas = strip_tags(item).strip().split('\n')
            if "Websites" in project:
                websites = strip_tags(project.split("Websites:")[1]).strip().split('\n')
            if "Website:" in project:
                websites = strip_tags(project.split("Website:")[1]).strip().split('\n')
            if "</ul>" in project:
                project_description = strip_tags(project.split("</ul>")[1].split("Website")[0])
            if project_name=="Poland" or project_name=="Netherlands" or project_name=="USA":
                return

            project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,'Social Innovation',%s,'MOPACT',4)"
            self.cursor.execute(project_sql, (project_name, websites[0]))
            self.db.commit()
            pro_id = self.cursor.lastrowid
            location_sql = "Insert into ProjectLocation(Type,Country,Projects_idProjects) VALUES('Main',%s,%s)"
            self.cursor.execute(location_sql, (project_country, pro_id))
            self.db.commit()
            sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_desc, (
                "Description", project_description, pro_id, source_page))
            self.db.commit()
            for area in project_areas:
                sql_domain = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
                self.cursor.execute(sql_domain, (
                "Domain", area, pro_id, source_page))
                self.db.commit()
            if len(websites) > 1:
                k = 0
                for w in websites:
                    if k == 0:
                        k = k + 1
                        continue
                    sql_web = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                              "VALUES(%s,%s,%s,NOW(),%s)"
                    self.cursor.execute(sql_web, (
                        "Additional WebSource", w, pro_id, source_page))
                    self.db.commit()

        print source_page