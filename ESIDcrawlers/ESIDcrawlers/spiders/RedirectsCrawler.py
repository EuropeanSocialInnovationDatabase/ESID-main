
from HTMLParser import HTMLParser
import MySQLdb

import scrapy
from flask import Request
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
    name = "RedirectsCrawler"
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
        sql = "Select idProjects,ProjectName,ProjectWebpage from Projects"
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

    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True, meta={
            'dont_redirect': True,
            'handle_httpstatus_list': [301, 302]
        })#,callback=self.parse_start_url)


    def parse_start_url(self, response):
        source_page = response.url
        if response.status == 301 or response.status==302:
            new_url = response.headers['Location']
            update_sql = "Update Projects set ProjectWebpage = '{0}' where ProjectWebpage= '{1}'".format(new_url,source_page)
            self.cursor.execute(update_sql)
            parsed = urlparse(new_url)
            domainA = '{uri.netloc}/'.format(uri=parsed).replace("/", "").replace("www.", "")
            self.allowed_domains.append(domainA)
            self.db.commit()
            #yield scrapy.Request(new_url, callback=self.parse_start_url,meta={'dont_filter':True})
            return
        return