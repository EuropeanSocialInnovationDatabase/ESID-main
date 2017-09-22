import scrapy
from HTMLParser import HTMLParser
import MySQLdb
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


class InnovageSpider(scrapy.Spider):
    name = "Innovage"

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = []

        for i in range(0,32):
            urls.append("http://www.innovage.group.shef.ac.uk/innovation-database.html?page="+str(i))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        #print response.url
        a_els = response.xpath('//a[@class="projectinfowrap"]')
        for a in a_els:
            new_url = a.xpath("@href").extract()
            url_to_crawl = "http://"+page +"/" +new_url[0]
            yield scrapy.Request(url=url_to_crawl, callback=self.parse_data)
        print "Elements:"+str(a_els)
    def parse_data(self,response):
        source_page = response.url
        projectname = response.xpath('//h1[@class="projectname"]/text()').extract()[0]
        organisation = " ".join(response.xpath('//section[@class="projectorganisationdetails"]/text()').extract())
        location = " ".join(response.xpath('//section[@class="projectorganisationdetails"]/span').extract())
        location_nohtml= strip_tags(location)
        location = location_nohtml[location_nohtml.index("Location")+9:location_nohtml.find('\r\n',10)]
        next_tab = location_nohtml.find('\r\n', 10)+4
        type = location_nohtml[location_nohtml.index("Type:") + 5:location_nohtml.find('\r\n', next_tab)]
        projectdetails = response.xpath('//div[@class="projectdetails printable"]')
        classification = " ".join(projectdetails.xpath('//section[@class="filtering"]').extract())
        classification_nohtml = strip_tags(classification)
        country = classification_nohtml[classification_nohtml.index("Country:") + 9:classification_nohtml.find('\r\n', classification_nohtml.index("Country:") + 10)]
        country = country.replace('\r','').replace('\n','').replace('\t','').replace(" ","")
        classification_nohtml = classification_nohtml[classification_nohtml.find('\r\n', classification_nohtml.index("Country:") + 10):]
        Domain = classification_nohtml[classification_nohtml.index("Domain:") + 7:classification_nohtml.find('\r\n',classification_nohtml.index("Domain:") + 9)]
        Domain = Domain.replace('\r', '').replace('\n', '').replace('\t', '').replace(" ","")
        Stage = classification_nohtml[
                 classification_nohtml.index("Stage:") + 6:classification_nohtml.find('\r\n',classification_nohtml.index("Stage:") + 8)]
        Stage = Stage.replace('\r', '').replace('\n', '').replace('\t', '')

        primary_impact = classification_nohtml[classification_nohtml.index("Primary Impact:") + 15:classification_nohtml.find('\r\n', classification_nohtml.index("Primary Impact:") + 18)]
        primary_impact = primary_impact.replace('\r','').replace('\n','').replace('\t','').replace(" ","")
        secondary_impact = classification_nohtml[
                classification_nohtml.index("Secondary Impact:") + 17:classification_nohtml.find('\r\n',
                                                                                     classification_nohtml.index(
                                                                                         "Secondary Impact:") + 19)]
        secondary_impact = secondary_impact.replace('\r', '').replace('\n', '').replace('\t', '').replace(" ","")
        additional_info = " ".join(projectdetails.xpath('//section[@class=""]').extract())
        web_site_html = " ".join(projectdetails.xpath('//section[@class=""]/descendant::*/a').extract())
        web_site = strip_tags(web_site_html).split('\n')
        if len(web_site) == 1:
            web_site = web_site[0].split(" ")
        project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,'Social Innovation',%s,'Innovage',3)"
        self.cursor.execute(project_sql,(projectname,web_site[0]))
        self.db.commit()
        pro_id = self.cursor.lastrowid
        location_sql = "Insert into ProjectLocation(Type,Country,Projects_idProjects) VALUES('Main',%s,%s)"
        self.cursor.execute(location_sql,(country,pro_id))
        self.db.commit()
        sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                         "VALUES(%s,%s,%s,NOW(),%s)"
        self.cursor.execute(sql_desc, (
        "Description", type, pro_id, source_page))
        self.db.commit()

        sql_domain = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                   "VALUES(%s,%s,%s,NOW(),%s)"
        self.cursor.execute(sql_domain, (
            "Domain", Domain, pro_id, source_page))
        self.db.commit()

        sql_stage = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                     "VALUES(%s,%s,%s,NOW(),%s)"
        self.cursor.execute(sql_stage, (
            "Stage", Stage, pro_id, source_page))
        self.db.commit()

        sql_additional = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                    "VALUES(%s,%s,%s,NOW(),%s)"
        self.cursor.execute(sql_stage, (
            "Additional Info", sql_additional, pro_id, source_page))
        self.db.commit()
        if len(web_site)>1:
            k = 0
            for w in web_site:
                if k==0:
                    k=k+1
                    continue
                sql_web = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                                 "VALUES(%s,%s,%s,NOW(),%s)"
                self.cursor.execute(sql_web, (
                    "Additional WebSource", w, pro_id, source_page))
                self.db.commit()
        sql_web = "Insert into OutreachImpact (Type,Name,Description,URL,Projects_idProjects)" \
                "VALUES(%s,%s,%s,%s,%s)"
        self.cursor.execute(sql_web, (
            "Impact", 'Primary Impact',primary_impact,source_page, pro_id))
        self.db.commit()
        sql_web = "Insert into OutreachImpact (Type,Name,Description,URL,Projects_idProjects)" \
                  "VALUES(%s,%s,%s,%s,%s)"
        self.cursor.execute(sql_web, (
            "Impact", 'Secondary Impact', secondary_impact, source_page, pro_id))
        self.db.commit()

        print country

        print organisation
        print projectname

        print source_page