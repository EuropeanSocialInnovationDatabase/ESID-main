
from HTMLParser import HTMLParser
import MySQLdb

import scrapy
from scrapy.linkextractors import LinkExtractor
from lxml.html.clean import Cleaner
from lxml.html.soupparser import fromstring
from lxml.etree import tostring
import re
import BeautifulSoup
import time
from scrapy.spiders import Rule, CrawlSpider

from database_access import *
import nltk
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

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' -+'.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class GeneralWebsiteRulespiderNew(CrawlSpider):
    name = "GeneralWebsiteRule_improved"
    allowed_domains = ["fablab.hochschule-rhein-waal.de"]
    start_urls = []

    def __init__(self, crawl_pages=True, moreparams=None, *args, **kwargs):
        super(GeneralWebsiteRulespiderNew, self).__init__(*args, **kwargs)
        # Set the GeneralWebsiteRulespider member from here
        if (crawl_pages is True):
            # Then recompile the Rules
            self.allowed_domains = self.get_allowed()
            self.start_urls = self.get_starting_urls()
            regs = []
            for dom in  self.start_urls:
                regs.append(dom+".*")
            GeneralWebsiteRulespiderNew.rules = (Rule(LinkExtractor(allow=regs), callback="parse_start_url", follow=True),)

            super(GeneralWebsiteRulespiderNew, self)._compile_rules()
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
        #             or "pinterest" in ArtWeb.lower() or "meetup" in ArtWeb.lower() or "wikipedia" in ArtWeb.lower() :
        #         continue
        # 
        #     parsed_uri = urlparse(ArtWeb)
        #     domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/","").replace("www.","")
        #     prog = re.compile(pattern)
        #     result = prog.match(domain)
        #     if result == None:
        #         continue
        #    allowed_domains.append(domain)
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
        #allowed_domains = ["fun-mooc.fr"]
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
        #         or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower() or "pinterest" in ArtWeb.lower() or "github" in ArtWeb.lower():
        #         continue
        #     prog = re.compile(pattern)
        #     result = prog.match(ArtWeb.lower())
        #     if result == None:
        #         continue
        #     start_urls.append(ArtWeb)
        sql = "Select idProjects,ProjectName,ProjectWebpage from Projects where idProjects=7584"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        urls = []
        start_urls = []
        for res in results:
            idActor = res[0]
            ArtName = res[1]
            ArtWeb = res[2]
            if ArtWeb == None or "vk.com" in ArtWeb.lower() or "youtube" in ArtWeb.lower() or "twitter" in ArtWeb.lower() or "linkedin" in ArtWeb.lower() \
                    or "vimeo" in ArtWeb.lower() or "instagram" in ArtWeb.lower() or "plus.google" in ArtWeb.lower() or "github" in ArtWeb.lower():
                continue
            prog = re.compile(pattern)
            result = prog.match(ArtWeb.lower())
            if result == None:
                continue
            start_urls.append(ArtWeb)
        #start_urls = ["https://www.fun-mooc.fr"]
        return start_urls


    def parse_start_url(self, response):
        source_page = response.url
        actorWeb = ""
        ProWeb = ""
        print source_page
        if "facebook.com" in source_page or "vk.com" in source_page or "youtube.com" in source_page or "twitter.com" in source_page or \
                        "linkedin" in source_page or "vimeo" in source_page or "instagram" in source_page or "google" in source_page \
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
        try:
            s = fromstring(response.body)
            cleaner = Cleaner()
            cleaner.javascript = True  # This is True because we want to activate the javascript filter
            cleaner.style = True
            s2 = cleaner.clean_html(s)
            inner_html = tostring(s2)
            item.Text = strip_tags(inner_html)
        except:
            # inner_html = BeautifulSoup.BeautifulSoup(response.body).text
            # item.Text = strip_tags(inner_html)
            soup = BeautifulSoup.BeautifulSoup(response.body)
            data = soup.findAll(text=True)
            result = filter(visible, data)
            content = ""
            prevN = False
            for r in result:
                if r == '\n' and prevN:
                    continue
                if r == '\n':
                    prevN = True
                else:
                    prevN = False
                content = content +' ' +r
            item.Text = content

        parsed_uri = urlparse(item.URL)
        domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
        isActor = False
        find_act_sql = "Select idActors,ActorName,ActorWebsite from Actors where ActorWebsite like '%" + domain + "%'"
        self.cursor.execute(find_act_sql)
        results = self.cursor.fetchall()
        isActor = False

        for res in results:
            item.RelatedTo = "Actor"
            item.DatabaseID = res[0]
            item.Name = res[1]
            actorWeb = res[2]
            isActor = True
            print "This is Actor with domain "+domain
            print item.Name
        if isActor == False:
            find_pro_sql = "Select idProjects,ProjectName,ProjectWebpage from Projects where ProjectWebpage like '%" + domain + "%'"
            self.cursor.execute(find_pro_sql)
            results = self.cursor.fetchall()
            smallest_distance = 1000
            for res in results:
                item.RelatedTo = "Project"
                ProWeb = res[2]
                edit_distance = nltk.edit_distance(source_page,ProWeb)
                if edit_distance<smallest_distance:
                    item.DatabaseID = res[0]
                    item.Name = res[1]
                    smallest_distance = edit_distance
                print "This is Project with domain " + domain
                print item.Name
        if ProWeb != source_page and actorWeb != source_page and domain != actorWeb and domain != ProWeb and "http://"+domain != actorWeb and "http://www."+domain != actorWeb and "https://"+domain != actorWeb and "https://www."+domain != actorWeb \
                and "http://" + domain != ProWeb and "http://www." + domain != ProWeb and "https://" + domain != ProWeb and "https://www." + domain != ProWeb:
            print "Returning: "+domain+"   "+source_page+"    "+actorWeb+"    "+ProWeb
            return

        if(item.DatabaseID == None or item.DatabaseID==""):
            return
        client = MongoClient()
        db = client.ESID

        result = db.test12.insert_one(
            {
                "timestamp":time.time(),
                "relatedTo": item.RelatedTo,
                "mysql_databaseID": str(item.DatabaseID),
                "name": item.Name,
                "url": item.URL,
                "page_title": item.PageTitle,
                "content": item.Content.decode('utf8',errors='ignore'),
                "text": item.Text
            }

        )
        yield item
        le = LinkExtractor()
        links = le.extract_links(response)
        for link in links:
            if "github" in link.url:
                continue
            else:
                yield scrapy.Request(link.url, callback=self.parse_start_url)