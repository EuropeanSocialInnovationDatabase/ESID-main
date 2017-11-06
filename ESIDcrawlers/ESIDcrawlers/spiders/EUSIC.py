import BeautifulSoup
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


class EUSICSpider(scrapy.Spider):
    name = "EUSIC"

    def start_requests(self):
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        urls = ["http://eusic-2016.challenges.org/selected/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        #print response.url
        a_els = response.xpath('//a[@class="w-inline-block finalist-card bee"]')
        for a in a_els:
            new_url = a.xpath("@href").extract()
            url_to_crawl = new_url[0]
            yield scrapy.Request(url=url_to_crawl, callback=self.parse_data)
    def parse_data(self,response):
        facebook = ""
        website = ""
        twitter = ""
        name = None
        source_page = response.url
        html = response.body.replace('\n', '').replace('\t', '').replace('\r', '')
        soup = BeautifulSoup.BeautifulSoup(html)
        divs = soup.findAll("div", {'class': 'content'})
        field = []
        for div in divs:
            if "essential info" in div.text.lower():
                parts = str(div).split("<br />")
                StartField = False
                for part in parts:
                    if "Semi-finalist:" in part or "Finalist:" in part or "Winner:" in part:
                        name = strip_tags(part).split(":")[1].replace('"','')
                    if "Country:" in part:
                        country = strip_tags(part).split(":")[1].replace('"','')
                    if StartField:
                        if "<a" not in part:
                            field.append(strip_tags(part))
                        elif "webpage" in part.lower():
                            webtag = BeautifulSoup.BeautifulSoup(part)
                            website = webtag.a['href']
                        elif "facebook" in part.lower():
                            webtag = BeautifulSoup.BeautifulSoup(part)
                            facebook = webtag.a['href']
                        elif "twitter" in part.lower():
                            webtag = BeautifulSoup.BeautifulSoup(part)
                            twitter = webtag.a['href']
                    if "Field:" in part:
                        field.append(strip_tags(part).split(":")[1].replace('"',''))
                        StartField = True
            if "summary" in div.text.lower():
                summary = str(div).replace("<br />",'\n').replace("Summary","")
                summary = strip_tags(summary).replace("View all semi-finalists","").strip()
        if  name is None:
            name = soup.findAll("h1")[0].text.lower()
        project_sql = "INSERT INTO Projects (ProjectName,Type,ProjectWebpage,FirstDataSource,DataSources_idDataSources,FacebookPage,ProjectTwitter) VALUES (%s,'Social Innovation',%s,'EUSIC',7,%s,%s)"
        self.cursor.execute(project_sql,(name,website,facebook,twitter))
        self.db.commit()
        pro_id = self.cursor.lastrowid

        sql_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                  "VALUES(%s,%s,%s,NOW(),%s)"
        self.cursor.execute(sql_desc, (
        "Description", summary, pro_id, source_page))
        self.db.commit()
        for f in field:
            sql_domain = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL)" \
                   "VALUES(%s,%s,%s,NOW(),%s)"
            self.cursor.execute(sql_domain, (
            "Domain", f, pro_id, source_page))
            self.db.commit()
        location_sql = "Insert into ProjectLocation(Type,Country,Projects_idProjects) VALUES('Main',%s,%s)"
        self.cursor.execute(location_sql,(country,pro_id))
        self.db.commit()
