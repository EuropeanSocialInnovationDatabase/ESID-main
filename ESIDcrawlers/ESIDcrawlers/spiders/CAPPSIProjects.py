import BeautifulSoup
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


def normalize_date(date):
    return_date = ""
    if "/" in date:
        dates = date.split("/")
        day = dates[0]
        month = dates[1]
        year = dates[2]
    else:
        if "Jan" in date:
            month = "01"
        if "Feb" in date:
            month = "02"
        if "Mar" in date:
            month = "03"
        if "Apr" in date:
            month = "04"
        if "May" in date:
            month = "05"
        if "Jun" in date:
            month = "06"
        if "Jul" in date:
            month = "07"
        if "Aug" in date:
            month = "08"
        if "Sep" in date:
            month = "09"
        if "Oct" in date:
            month = "10"
        if "Nov" in date:
            month = "11"
        if "Dec" in date:
            month = "12"
        day = "01"
        m = re.search('\d\d\d\d', date)
        print date
        year = m.group(0)
    return_date = year.replace(" ","") + "-"+month.replace(" ","")+"-"+day.replace(" ","")
    return return_date


class CAPPSIpider(scrapy.Spider):
    name = "CAPPSI"

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = ["https://capssi.eu/caps-projects/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        #print response.url
        a_els = response.xpath('//a[@class="element-wrap"]')
        for a in a_els:
            new_url = a.xpath("@href").extract()
            url_to_crawl = new_url[0]
            yield scrapy.Request(url=url_to_crawl, callback=self.parse_data)
    def parse_data(self,response):
        source_page = response.url
        html = response.body.replace('\n', '').replace('\t', '').replace('\r', '')
        soup = BeautifulSoup.BeautifulSoup(html)
        divs = soup.findAll("div", {'class': 'wrap-content'})
        field = []
        project_lifetime = ""
        project_website = ""
        project_desc = ""
        project_title = ""
        for div in divs:
            if "CAPSSI" in div.text or "ChiC Project" in div.text:
                continue
            title = soup.findAll("h1")
            project_title =  strip_tags(title[0].text)
            ps = div.findAll("p")
            for p in ps:
                if "Project lifetime" in p.text:
                    project_lifetime = project_lifetime + p.text.split("Project lifetime:")[1]
                elif "Website" in p.text:
                    project_website = p.a['href']
                else:
                    project_desc = project_desc + p.text
            project_lifetime = project_lifetime.replace("Project lifetime:","")
            if " to " in project_lifetime:
                dates = project_lifetime.split("to")
            elif " - " in project_lifetime:
                dates = project_lifetime.split("-")
            elif " &#8211; " in project_lifetime:
                dates = project_lifetime.split("&#8211;")
            if dates == None or len(dates)<2:
                start_date = None
                end_date = None
            else:
                start_date = normalize_date(dates[0])
                end_date = normalize_date(dates[1])
            project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,DateStart,DateEnd,FirstDataSource,DataSources_idDataSources) VALUES (%s,'Social Innovation',%s,%s,%s,'CAPPSI projects',14)"
            self.cursor.execute(project_sql,(project_title,project_website,start_date,end_date))
            self.db.commit()
            pro_id = self.cursor.lastrowid
            sql_contact = "Insert into ActorsAdditionalData (FieldName,FieldContent,Actors_idActors,DateObtained,SourceURL)" \
                          "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_contact, (
                "Description", project_desc, pro_id,
                source_page))
            self.db.commit()
        #     if "essential info" in div.text.lower():
        #         parts = str(div).split("<br />")
        #         StartField = False
        #         for part in parts:
        #             if "Semi-finalist:" in part or "Finalist:" in part or "Winner:" in part:
        #                 name = strip_tags(part).split(":")[1].replace('"','')
        #             if "Country:" in part:
        #                 country = strip_tags(part).split(":")[1].replace('"','')
        #             if StartField:
        #                 if "<a" not in part:
        #                     field.append(strip_tags(part))
        #                 elif "webpage" in part.lower():
        #                     webtag = BeautifulSoup.BeautifulSoup(part)
        #                     website = webtag.a['href']
        #                 elif "facebook" in part.lower():
        #                     webtag = BeautifulSoup.BeautifulSoup(part)
        #                     facebook = webtag.a['href']
        #                 elif "twitter" in part.lower():
        #                     webtag = BeautifulSoup.BeautifulSoup(part)
        #                     twitter = webtag.a['href']
        #             if "Field:" in part:
        #                 field.append(strip_tags(part).split(":")[1].replace('"',''))
        #                 StartField = True
        #     if "summary" in div.text.lower():
        #         summary = str(div).replace("<br />",'\n').replace("Summary","")
        #         summary = strip_tags(summary).replace("View all semi-finalists","").strip()
        # if  name is None:
        #     name = soup.findAll("h1")[0].text.lower()
        # project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources,FacebookPage,ProjectTwitter) VALUES (%s,'Social Innovation',%s,'EUSIC',7,%s,%s)"
        # self.cursor.execute(project_sql,(name,website,facebook,twitter))
        # self.db.commit()
        # pro_id = self.cursor.lastrowid
        #
        # sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
        #           "VALUES(%s,%s,%s,NOW(),%s)"
        # self.cursor.execute(sql_desc, (
        # "Description", summary, pro_id, source_page))
        # self.db.commit()
        # for f in field:
        #     sql_domain = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
        #            "VALUES(%s,%s,%s,NOW(),%s)"
        #     self.cursor.execute(sql_domain, (
        #     "Domain", f, pro_id, source_page))
        #     self.db.commit()
        # location_sql = "Insert into ProjectLocation(Type,Country,Projects_idProjects) VALUES('Main',%s,%s)"
        # self.cursor.execute(location_sql,(country,pro_id))
        # self.db.commit()
