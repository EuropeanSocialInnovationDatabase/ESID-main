#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from HTMLParser import HTMLParser
import MySQLdb
from database_access import *
from scrapy.linkextractors import LinkExtractor
import re
import os

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


class KickstarterCrawler2(scrapy.Spider):
    name = "KickstarterCrawler2"
    num = 0
    allowed_domains = ['www.kickstarter.com']
    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = ["https://www.kickstarter.com/discover/",
                "https://www.kickstarter.com/",
                "https://www.kickstarter.com/discover/advanced?sort=magic&seed=2605334&page=1",
                "https://www.kickstarter.com/discover/advanced?sort=magic&seed=2605334&page=2",
                "https://www.kickstarter.com/discover/advanced?sort=magic&seed=2605334&page=3",
                "https://www.kickstarter.com/discover/advanced?sort=magic&seed=2605334&page=4",
                "https://www.kickstarter.com/discover/pwl?ref=discovery_overlay"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        dirName = "Crawled/"
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        source_page = response.url
        try:
            le = LinkExtractor()
            links = le.extract_links(response)
            print(links)
            firstPage = False
            for link in links:
                if "github" in link.url:
                    continue
                else:
                    print(link.url)
                    yield scrapy.Request(link.url, callback=self.parse)
        except:
            print "No links"
        if "https://www.kickstarter.com/projects/" not in source_page:
            return
        body = response.body.strip().replace("  "," ")
        ptitle = response.xpath('//h2/text()').extract()
        desc = response.xpath('//p[contains(@class, "project-description")]/text()').extract()
        long_desc = response.xpath('//div[contains(@class,"full-description")]/p//text()').extract()
        ldesc = ""
        for ld in desc:
            ldesc = ldesc + " "+ld.encode('utf-8') + "\n"
        for ld in long_desc:
            ldesc = ldesc + " "+ld.encode('utf-8') + "\n"
        project_title = ptitle[0].replace("'","").replace('"','')
        if len(project_title)>5 and len(ldesc)>200:
            project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources,Exclude) VALUES (%s,'Kickstarter project',%s,'Kickstarter',70,1)"
            self.cursor.execute(project_sql, (project_title, ""))
            self.db.commit()
            pro_id = self.cursor.lastrowid
            sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_desc, (
                "Description", ldesc.replace("'","").replace('"',''), pro_id, source_page))
            self.db.commit()

            marks_sql = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,Social_Innovation_overall,SourceModel) VALUES ('0','0','0','0',%s,'0','Manual_Kickstarter')"
            self.cursor.execute(marks_sql,(pro_id,))
            self.db.commit()