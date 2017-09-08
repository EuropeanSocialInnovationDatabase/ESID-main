import MySQLdb
from HTMLParser import HTMLParser
import BeautifulSoup

import scrapy

from database_access import *


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


class SimraSpider(scrapy.Spider):
    name = "Simra"

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = []

        for i in range(0,500):
            urls.append("http://www.simra-h2020.eu/index.php/description/?id="+str(i))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_data)


    def parse_data(self,response):
        source_page = response.url
        name = strip_tags(response.xpath('//h2[@class="textgr"]').extract()[0])
        if name == "":
            return
        html = response.body.replace('\n','').replace('\t','').replace('\r','')
        soup = BeautifulSoup.BeautifulSoup(html)
        print soup.title
        labels = soup.findAll("label",{'class':'tres'})
        for label in labels:
            if "starting year:" in label.text.lower():
                starting_year = label.parent.input['value']
            if "scale:" in label.text.lower():
                scale = label.parent.input['value']
            if "region:" in label.text.lower():
                region = label.parent.input.nextSibling.nextSibling['value']
            if "type of mra:" in label.text.lower():
                mra_type = label.parent.input.nextSibling.nextSibling.nextSibling.nextSibling['value']
            if "location:" in label.text.lower():
                city = label.parent.input['value']
                country = label.parent.input.nextSibling.nextSibling['value']
            if "sector:" in label.text.lower():
                sector = label.parent.input['value']
                topic = label.parent.input.nextSibling.nextSibling['value']
            if "challenges addressed:" in label.text.lower():
                challenges = label.parent.div.text
            if "description:" in label.text.lower():
                description = label.parent.div.text
            if "form:" in label.text.lower():
                form = label.parent.input['value']
                actors = label.parent.input.nextSibling.nextSibling['value']
            if "practices:" in label.text.lower():
                practices = label.parent.div.text
                actors_members = label.parent.div.nextSibling.text
            if "social change" in label.text.lower():
                social_change = label.parent.div.text
            if "website" in label.text.lower():
                content = label.parent.a.contents
                websites = []
                for con in content:
                    if con!=None:
                        if hasattr(con,'name')==True:
                            continue
                        websites.append(con)
            if "references:" in label.text.lower():
                references = label.parent.div.text
        # print name              #Projects/Actors.ProjectName
        # print starting_year     # Projects/Actors.DateStart
        # print scale             # AdditionalProjectData/ActorsAddionalData.Scale
        # print region            # AdditionalProjectData/ActorsAddionalData.Region
        # print mra_type          # AdditionalProjectData/ActorsAddionalData.MRA_Type
        # print city              #Location/ProjectLocation.City
        # print country           #Location/ProjectLocation.Country
        # print sector            # AdditionalProjectData/ActorsAddionalData.Sector
        # print topic             # AdditionalProjectData/ActorsAddionalData.Topic
        # print challenges        # AdditionalProjectData/ActorsAddionalData.ChallengesAddressed
        # print description       # AdditionalProjectData/ActorsAddionalData.Description
        # print form              # AdditionalProjectData/ActorsAddionalData.Form
        # print actors            # AdditionalProjectData/ActorsAddionalData.Actors
        # print actors_members    # AdditionalProjectData/ActorsAddionalData.ActorMembers
        # print practices         # AdditionalProjectData/ActorsAddionalData.Practices
        # print social_change     # AdditionalProjectData/ActorsAddionalData.SocialChange
        # print websites          # AdditionalProjectData/ActorsAddionalData.Websites + main website
        # print references        # AdditionalProjectData/ActorsAddionalData.References
        if starting_year=="":
            starting_year=None
        else:
            starting_year=starting_year+"-01-01"
        if form == 'Project' or 'project' in name.lower():
            if (len(websites) > 0):
                project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources,DateStart) VALUES (%s,'Social Innovation',%s,'Simra',5,%s)"
                self.cursor.execute(project_sql,(name,websites[0],starting_year))
                self.db.commit()
            else:
                project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources,DateStart) VALUES (%s,'Social Innovation',%s,'Simra',5,%s)"
                self.cursor.execute(project_sql, (name, "", starting_year ))
                self.db.commit()
            pro_id = self.cursor.lastrowid
            location_sql = "Insert into ProjectLocation(Type,City,Country,Projects_idProjects) VALUES('Main',%s,%s,%s)"
            self.cursor.execute(location_sql,(city,country,pro_id))
            self.db.commit()
            sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                 "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_desc, (
            "Description", description, pro_id, source_page))
            self.db.commit()
            sql_scale = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_scale, (
                "Scale", scale, pro_id, source_page))
            self.db.commit()
            sql_region = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                        "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_region, (
                "Region", region, pro_id, source_page))
            self.db.commit()
            sql_mra_type = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_mra_type, (
                "MRA Type", mra_type, pro_id, source_page))
            self.db.commit()
            sql_sector = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_sector, (
                "Sector", sector, pro_id, source_page))
            self.db.commit()
            sql_topic = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_topic, (
                "Topic", topic, pro_id, source_page))
            self.db.commit()
            sql_challenges = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                        "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_challenges, (
                "Challenges Addressed", challenges, pro_id, source_page))
            self.db.commit()
            sql_actors = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_actors, (
                "Actors", actors, pro_id, source_page))
            self.db.commit()
            sql_actors_members = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_actors_members, (
                "Actors Expanded", actors_members, pro_id, source_page))
            self.db.commit()
            sql_practices = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                 "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_practices, (
                "Practices", practices, pro_id, source_page))
            self.db.commit()
            sql_social_change = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                            "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_social_change, (
                "Social Change", social_change, pro_id, source_page))
            self.db.commit()
            sql_references = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_references, (
                "Social Change", references, pro_id, source_page))
            self.db.commit()
            sql_form = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_form, (
                "Form", form, pro_id, source_page))
            self.db.commit()
            if len(websites) > 1:
                k = 0
                for w in websites:
                    if k==0:
                        k=k+1
                        continue
                    sql_websites = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                     "VALUES(%s,%s,%s,NOW(),%s)"
                    self.cursor.execute(sql_websites, (
                        "Additional WebSource", w, pro_id, source_page))
                    self.db.commit()
        else:
            if(len(websites)>0):
                project_sql = "INSERT INTO Actors (ActorName,Type,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources,StartDate,SubType) VALUES (%s,'S',%s,'Simra',5,%s,%s)"
                self.cursor.execute(project_sql, (name, websites[0], starting_year,form))
                self.db.commit()
            else:
                project_sql = "INSERT INTO Actors (ActorName,Type,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources,StartDate,SubType) VALUES (%s,'S',%s,'Simra',5,%s,%s)"
                self.cursor.execute(project_sql, (name, "", starting_year ,form))
                self.db.commit()
            pro_id = self.cursor.lastrowid
            location_sql = "Insert into Location(Type,City,Country,Actors_idActors) VALUES('Main',%s,%s,%s)"
            self.cursor.execute(location_sql, (city, country, pro_id))
            self.db.commit()
            sql_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_desc, (
                "Description", description, pro_id, source_page))
            self.db.commit()
            sql_scale = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                        "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_scale, (
                "Scale", scale, pro_id, source_page))
            self.db.commit()
            sql_region = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_region, (
                "Region", region, pro_id, source_page))
            self.db.commit()
            sql_mra_type = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_mra_type, (
                "MRA Type", mra_type, pro_id, source_page))
            self.db.commit()
            sql_sector = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_sector, (
                "Sector", sector, pro_id, source_page))
            self.db.commit()
            sql_topic = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                        "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_topic, (
                "Topic", topic, pro_id, source_page))
            self.db.commit()
            sql_challenges = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_challenges, (
                "Challenges Addressed", challenges, pro_id, source_page))
            self.db.commit()
            sql_actors = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_actors, (
                "Actors", actors, pro_id, source_page))
            self.db.commit()
            sql_actors_members = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                                 "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_actors_members, (
                "Actors Expanded", actors_members, pro_id, source_page))
            self.db.commit()
            sql_practices = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                            "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_practices, (
                "Practices", practices, pro_id, source_page))
            self.db.commit()
            sql_social_change = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                                "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_social_change, (
                "Social Change", social_change, pro_id, source_page))
            self.db.commit()
            sql_references = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                             "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_references, (
                "Social Change", references, pro_id, source_page))
            self.db.commit()
            sql_form = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                       "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_form, (
                "Form", form, pro_id, source_page))
            self.db.commit()
            if len(websites) > 1:
                k = 0
                for w in websites:
                    if k == 0:
                        k = k + 1
                        continue
                    sql_websites = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                                   "VALUES(%s,%s,%s,NOW(),%s)"
                    self.cursor.execute(sql_websites, (
                        "Additional WebSource", w, pro_id, source_page))
                    self.db.commit()
            pass

        print source_page