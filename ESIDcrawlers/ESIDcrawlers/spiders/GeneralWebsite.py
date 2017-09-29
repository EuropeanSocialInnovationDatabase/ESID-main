
from HTMLParser import HTMLParser
import MySQLdb
from scrapy.linkextractors import LinkExtractor
from lxml.html.clean import Cleaner
from lxml.html.soupparser import fromstring
from lxml.etree import tostring
import re

from scrapy.spiders import Rule, CrawlSpider

from database_access import *
import requests
import json
from urlparse import urlparse, urljoin
from pymongo import MongoClient

class SIScrapedItem():
    RelatedTo = ""
    Name = ""
    DatabaseID = ""
    Date = ""
    URL = ""
    Content = ""
    Text = ""
    PageTitle = ""



class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class GeneralWebsitespider(CrawlSpider):
    name = "GeneralWebsite"
    allowed_domains = ["fablab.hochschule-rhein-waal.de"]
    start_urls = []

    def __init__(self, crawl_pages=True, moreparams=None, *args, **kwargs):
        super(GeneralWebsitespider, self).__init__(*args, **kwargs)
        # Set the class member from here
        if (crawl_pages is True):

            # Then recompile the Rules
            self.allowed_domains = self.get_allowed()
            self.start_urls = self.get_starting_urls()
            regs = []
            for dom in  self.start_urls:
                regs.append(dom+".*")
            GeneralWebsitespider.rules = (Rule(LinkExtractor(allow=regs), callback="parse_start_url", follow=True),)

            super(GeneralWebsitespider, self)._compile_rules()
        self.moreparams = moreparams



    def get_allowed(self):
        allowed_domains = []
        pattern = "[a-zA-Z0-9]*[\.]{0,1}[a-zA-Z0-9]+[\.][a-zA-Z0-9]{0,4}"
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        # sql = "Select idActors,ActorName,ActorWebsite from Actors"
        # self.cursor.execute(sql)
        # results = self.cursor.fetchall()
        # for res in results:
        #     ArtWeb = res[2]
        #     if ArtWeb== None or "vk.com" in ArtWeb.lower() or "youtube" in ArtWeb.lower() or "twitter" in ArtWeb.lower() or "linkedin" in ArtWeb.lower() \
        #         or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower() or "facebook.com" in ArtWeb.lower() \
        #             or "pinterest" in ArtWeb.lower() or "meetup" in ArtWeb.lower() or "wikipedia" in ArtWeb.lower():
        #         continue
        #
        #     parsed_uri = urlparse(ArtWeb)
        #     domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/","").replace("www.","")
        #     prog = re.compile(pattern)
        #     result = prog.match(domain)
        #     if result == None:
        #         continue
        #     allowed_domains.append(domain)
        sql = "Select idProjects,ProjectName,ProjectWebpage from Projects"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for res in results:
            ArtWeb = res[2]
            if ArtWeb == None or "vk.com" in ArtWeb.lower() or "youtube" in ArtWeb.lower() or "twitter" in ArtWeb.lower() or "linkedin" in ArtWeb.lower() \
                    or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower() or "facebook.com" in ArtWeb.lower()\
                    or "pinterest" in ArtWeb.lower() or "meetup" in ArtWeb.lower()or "wikipedia" in ArtWeb.lower():
                continue
            parsed_uri = urlparse(ArtWeb)
            try:
                domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
                prog = re.compile(pattern)
                result = prog.match(domain)
                if result == None:
                    continue
                allowed_domains.append(domain)
            except:
                print "Domain with special character: "+ArtWeb
        return allowed_domains


    def get_starting_urls(self):
        pattern = "http[s]{0,1}://[a-zA-Z0-9]*[\.]{0,1}[a-zA-Z0-9]+[\.][a-zA-Z0-9]{0,4}"
        start_urls = []
        self.db = MySQLdb.connect(host, username, password, database, charset='utf8')
        self.cursor = self.db.cursor()
        # sql = "Select idActors,ActorName,ActorWebsite from Actors"
        # self.cursor.execute(sql)
        # results = self.cursor.fetchall()
        # urls = []
        # for res in results:
        #     idActor = res[0]
        #     ArtName = res[1]
        #     ArtWeb = res[2]
        #     if ArtWeb== None or "vk.com" in ArtWeb.lower() or "youtube" in ArtWeb.lower() or "twitter" in ArtWeb.lower() or "linkedin" in ArtWeb.lower() \
        #         or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower() or "pinterest" in ArtWeb.lower() :
        #         continue
        #     prog = re.compile(pattern)
        #     result = prog.match(ArtWeb.lower())
        #     if result == None:
        #         continue
        #     start_urls.append(ArtWeb)
        sql = "Select idProjects,ProjectName,ProjectWebpage from Projects"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        urls = []
        for res in results:
            idActor = res[0]
            ArtName = res[1]
            ArtWeb = res[2]
            if ArtWeb == None or "vk.com" in ArtWeb.lower() or "youtube" in ArtWeb.lower() or "twitter" in ArtWeb.lower() or "linkedin" in ArtWeb.lower() \
                    or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower():
                continue
            prog = re.compile(pattern)
            result = prog.match(ArtWeb.lower())
            if result == None:
                continue
            start_urls.append(ArtWeb)
        return start_urls


    def parse_start_url(self, response):
        source_page = response.url
        print source_page
        if "facebook.com" in source_page or "vk.com" in source_page or "youtube.com" in source_page or "twitter.com" in source_page or \
                        "linkedin" in source_page or "vimeo" in source_page or "instagram" in source_page or "google" in source_page or "github" in source_page\
                or "pinterest" in source_page:
            return

        all_page_links = response.xpath('//a/@href').extract()
        item = SIScrapedItem()
        item.URL = source_page
        ptitle = response.xpath('//title').extract()
        if len(ptitle)>0:
            item.PageTitle = strip_tags(response.xpath('//title').extract()[0])
        else:
            item.PageTitle = ""
        item.Content = response.body
        s = fromstring(response.body)
        cleaner = Cleaner()
        cleaner.javascript = True  # This is True because we want to activate the javascript filter
        cleaner.style = True
        s2 = cleaner.clean_html(s)
        inner_html = tostring(s2)
        item.Text = strip_tags(inner_html)
        parsed_uri = urlparse(item.URL)
        domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
        isActor = False
        # find_act_sql = "Select idActors,ActorName,ActorWebsite from Actors where ActorWebsite like '%" + domain + "%'"
        # self.cursor.execute(find_act_sql)
        # results = self.cursor.fetchall()
        # isActor = False
        # for res in results:
        #     item.RelatedTo = "Actor"
        #     item.DatabaseID = res[0]
        #     item.Name = res[1]
        #     isActor = True
        #     print "This is Actor with domain "+domain
        #     print item.Name
        if isActor == False:
            find_pro_sql = "Select idProjects,ProjectName,ProjectWebpage from Projects where ProjectWebpage like '%" + domain + "%'"
            self.cursor.execute(find_pro_sql)
            results = self.cursor.fetchall()
            for res in results:
                item.RelatedTo = "Project"
                item.DatabaseID = res[0]
                item.Name = res[1]
                print "This is Project with domain " + domain
                print item.Name
        if(item.DatabaseID == None or item.DatabaseID==""):
            return
        client = MongoClient()
        db = client.ESID

        result = db.projects.insert_one(
            {
                "relatedTo": item.RelatedTo,
                "mysql_databaseID": str(item.DatabaseID),
                "name": item.Name,
                "url": item.URL,
                "page_title": item.PageTitle,
                "content": item.Content,
                "text": item.Text
            }

        )
        # Convert each Relative page link to Absolute page link -> /abc.html -> www.domain.com/abc.html and then send Request object
        # for relative_link in all_page_links:
        #
        #     print "relative link procesed:" + relative_link
        #     parsed_uri = urlparse(source_page)
        yield item