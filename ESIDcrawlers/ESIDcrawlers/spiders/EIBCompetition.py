
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


class EIBCompetitionspider(CrawlSpider):
    name = "EIBCompetition"
    allowed_domains = ["adoptaunabuelo.org","arborea.io","www.coloradd.net","www.discovering-hands.de","givevision.net",
                  "www.kaitiaki.it","www.magikme.net","www.mycarematters.org","www.refugeeswork.at","www.freebirdclub.com",
                  "www.ultraspecialisti.com","www.walkwithpath.com","www.iosmosi.com",
                  "www.edukit.org.uk","sharingacademy.com","www.silentsecret.com","www.aprendicesvisuales.org","www.biocarbonengineering.com",
                  "www.lazzus.com","www.desolenator.com","www.mycarematters.org","ithacalaundry.gr","www.fitforkids.dk",
                  "www.feelif.com","www.bgood.at","blitab.com","www.designbypana.com","www.ecosia.org",
                  "www.fitforkids.dk","www.koiki.eu","www.letsgetsporty.com","www.marioway.it",
                  "peppypals.com","bluebadgestyle.com","www.adie.org","www.clear-village.org","thedoschool.org",
                  "helioz.org","www.mattecentrum.se","www.1toit2ages.be","www.bikway.com",
                  "buuv.nu","organery.co","www.ortialti.com","theyardtheatre.co.uk"]
    start_urls = ["https://adoptaunabuelo.org/","http://arborea.io","http://www.coloradd.net/","http://www.discovering-hands.de/en/","http://givevision.net/",
                  "http://www.kaitiaki.it/en/","https://www.magikme.net/","https://www.mycarematters.org/","https://www.refugeeswork.at/","https://www.freebirdclub.com/",
                  "http://www.ultraspecialisti.com/?lang=en","https://www.walkwithpath.com/","http://www.iosmosi.com/en/",
                  "https://www.edukit.org.uk/","https://sharingacademy.com/en","http://www.silentsecret.com","http://www.aprendicesvisuales.org/en/","http://www.biocarbonengineering.com",
                  "http://www.lazzus.com/","http://www.desolenator.com/","https://www.mycarematters.org/","http://ithacalaundry.gr/en/home","http://www.fitforkids.dk/en/",
                  "https://www.feelif.com/","https://www.bgood.at/","http://blitab.com/","http://www.designbypana.com/","https://www.ecosia.org/",
                  "http://www.fitforkids.dk/en/","http://www.koiki.eu/en/","http://www.letsgetsporty.com/","http://www.marioway.it/word/en",
                  "http://peppypals.com/","https://bluebadgestyle.com/","https://www.adie.org/microfinance-in-france","http://www.clear-village.org","https://thedoschool.org/",
                  "http://helioz.org/","https://www.mattecentrum.se/om-oss/about-mattecentrum","http://www.1toit2ages.be/en/home.html","http://www.bikway.com/",
                  "https://buuv.nu/info/english","http://organery.co/","http://www.ortialti.com/en/","https://theyardtheatre.co.uk/"]

    def __init__(self, crawl_pages=True, moreparams=None, *args, **kwargs):
        super(EIBCompetitionspider, self).__init__(*args, **kwargs)
        # Set the class member from here
        if (crawl_pages is True):
            regs = []
            for dom in  self.start_urls:
                regs.append(dom+".*")
            EIBCompetitionspider.rules = (Rule(LinkExtractor(allow=regs), callback="parse_start_url", follow=True),)

            super(EIBCompetitionspider, self)._compile_rules()
        self.moreparams = moreparams




    def parse_start_url(self, response):
        source_page = response.url
        print source_page
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
        client = MongoClient()
        db = client.ESID

        result = db.EIBCompetition.insert_one(
            {
                "relatedTo": "Project",
                "domain": domain,
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