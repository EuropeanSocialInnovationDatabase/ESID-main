import BeautifulSoup
import scrapy
from HTMLParser import HTMLParser
import MySQLdb
from database_access import *
import requests
import json

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


class Gatespider(scrapy.Spider):
    name = "Gates"

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = []
        for i in range(1, 7):
            r = requests.post("https://www.gatesfoundation.org/services/gfo/search.ashx", data=json.dumps(
                {"freeTextQuery": "",
                 "fieldQueries": "(@gfotopics==\"Community Grants\") and (@gfomediatype==\"Grant\")", "page": str(i),
                 "resultsPerPage": "1000", "sortBy": "gfodate", "sortDirection": "desc"}))
            print(r.status_code, r.reason)
            json_text = json.loads(r.text)
            res = json_text["results"]
            for r in res:
                urls.append(r['url'])
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        source_page = response.url
        html = response.body.replace('\n', '').replace('\t', '').replace('\r', '')
        soup = BeautifulSoup.BeautifulSoup(html)
        article = soup.findAll("div",{'class': 'articleWrapper'})[0]
        name = strip_tags(str(article.findAll("h2")[0]))
        purpose = ""
        topic  =""
        amount = ""
        term = ""
        program = ""
        location  = ""
        topic = ""
        website = ""
        lines = str(article).split("<br />")
        for line in lines:
            if "Date:" in line:
                date = strip_tags(line.split(":")[1]).strip()
                m_y = date.split(" ")
                year = m_y[1]
                month = 1
                if m_y[0]=="January":
                    month = 1
                elif m_y[0]=="February":
                    month = 2
                elif m_y[0]=="March":
                    month = 3
                elif m_y[0]=="April":
                    month = 4
                elif m_y[0]=="May":
                    month = 5
                elif m_y[0]=="June":
                    month = 6
                elif m_y[0]=="July":
                    month = 7
                elif m_y[0]=="August":
                    month = 8
                elif m_y[0]=="September":
                    month = 9
                elif m_y[0]=="October":
                    month = 10
                elif m_y[0]=="November":
                    month = 11
                elif m_y[0]=="December":
                    month = 12
                startdate = year+"-"+str(month)+"-"+"1"
            if("Purpose:" in line):
                purpose = strip_tags(line.split(":")[1])
            if ("Amount:" in line):
                amount = strip_tags(line.split(":")[1])
            if ("Term:" in line):
                term = strip_tags(line.split(":")[1])
            if ("Topic:" in line):
                topic = strip_tags(line.split(":")[1])
            if ("Program:" in line):
                program = strip_tags(line.split(":")[1])
            if ("Location:" in line):
                location = strip_tags(line.split(":")[1])
            if ("Website:" in line):
                w = BeautifulSoup.BeautifulSoup(line)
                website = w.findAll("a")[0]["href"]
        print name

        test_sql = 'SELECT * FROM EDSI.Actors where ActorName like "%'+name+'%"';
        result = self.cursor.execute(test_sql)
        data = self.cursor.fetchall()
        if (len(data)==0):
            project_sql = "INSERT INTO Actors (ActorName,Type,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources,StartDate) VALUES (%s,'S',%s,'Bill and Melinda Gates Foundation',8,%s)"
            self.cursor.execute(project_sql, (name, website, startdate))
            self.db.commit()
            act_id = self.cursor.lastrowid
            sql_tag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_tag_desc, (
                "Purpose", purpose, act_id,
                "https://www.gatesfoundation.org"))
            self.db.commit()
            sql_tag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_tag_desc, (
                "Amount", amount, act_id,
                "https://www.gatesfoundation.org"))
            self.db.commit()
            sql_tag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_tag_desc, (
                "Term", term, act_id,
                "https://www.gatesfoundation.org"))
            self.db.commit()
            sql_tag_desc = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                           "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_tag_desc, (
                "Topic", topic, act_id,
                "https://www.gatesfoundation.org"))
            self.db.commit()
            self.cursor.execute(sql_tag_desc, (
                "Program", program, act_id,
                "https://www.gatesfoundation.org"))
            self.db.commit()
            sql_loc = "Insert into Location (Type,City,Actors_idActors) VALUES " \
                      "(%s,%s,%s)"
            self.cursor.execute(sql_loc, ("Headquarters", location, act_id))
