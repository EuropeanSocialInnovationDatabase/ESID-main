
from HTMLParser import HTMLParser
import MySQLdb
from scrapy.linkextractors import LinkExtractor
from lxml.html.clean import Cleaner
from lxml.html.soupparser import fromstring
from lxml.etree import tostring
from HTMLParser import HTMLParser
import BeautifulSoup
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

def convert2unicode(mydict):
    for k, v in mydict.iteritems():
        if isinstance(v, str):
            mydict[k] = unicode(v, errors = 'replace')
        elif isinstance(v, dict):
            convert2unicode(v)
class EIBCompetitionspider(CrawlSpider):
    name = "EIBCompetition2"
    allowed_domains = ["adoptaunabuelo.org","arborea.io","www.coloradd.net","www.discovering-hands.de","givevision.net",
                  "www.kaitiaki.it","www.magikme.net","www.mycarematters.org","www.refugeeswork.at","freebirdclub.com",
                  "www.ultraspecialisti.com","www.walkwithpath.com","www.iosmosi.com",
                  "www.edukit.org.uk","sharingacademy.com","www.silentsecret.com","www.aprendicesvisuales.org","www.biocarbonengineering.com",
                  "www.lazzus.com","www.desolenator.com","www.mycarematters.org","ithacalaundry.gr","www.fitforkids.dk",
                  "www.feelif.com","www.bgood.at","blitab.com","www.designbypana.com","www.ecosia.org",
                  "www.fitforkids.dk","www.koiki.eu","www.letsgetsporty.com","www.marioway.it",
                  "peppypals.com","bluebadgestyle.com","www.adie.org","www.clear-village.org","thedoschool.org",
                  "helioz.org","www.mattecentrum.se","www.1toit2ages.be","www.bikway.com",
                  "buuv.nu","organery.co","www.ortialti.com","theyardtheatre.co.uk",
                       "bincome.eu","bc4gd.com","wikihouse.cc","collaction.org","cultivai.com","www.thirdageireland.ie","www.feelif.com",
                       "www.leapslab.com","www.inclu-sight.com","fightthestroke.org","www.dialogue-se.com","mouse4all.com"
                       "www.openbiomedical.org","www.scribeasy.com","saga.one","siboxapp.com","www.signly.co","solomon.gr","www.barrabes.biz",
                       "www.wayfindr.net","action.neweconomics.org","www.cucula.org","www.themachinetobeanother.org","aid.technology",
                       "www.micro-rainbow.org","www.solidaritysalt.com","thebikeproject.co.uk","www.adamantbionrg.com","habibi.at","www.mygrantour.org",
                       "coreorient.com","www.refugeeswork.at","www.learningunlimited.co","wedocare.dei.uc.pt","www.thefreebirdclub.com","www.wheeliz.com",
                       "melawear.de","jakodoma.org","www.ssmsapp.com","www.galiboff.com","www.roda.hr","instituteintercer.org","www.loveyourwaste.com","crowdfundhq.com",
                       "www.cfmitalia.it","www.tasksquadhq.com","www.hazelheartwood.com","theurbanfarmer.co","www.happyfeetpreschool.net","www.scn.org","www.ipn.pt",
                       "grc.engineering.cf.ac.uk","www.science-link.eu","www.biobasenwe.org","www.innove.ee","www.greenpolis.fi","seap-alps.eu","www.cteg.org.uk",
                       "www.eoi.es","mka.malopolska.pl","www.olsztyn.eu","exeko.org","www.rdsp.com","www.rootsofempathy.org","janeswalk.org","www.jumpmath.org",
                       "www.simprints.com","hippogriff.se"]

    start_urls = [ "http://www.openbiomedical.org/"

        # "https://mka.malopolska.pl/en/",
        # "http://www.westseattlefoodbank.org/",
        #           "https://adoptaunabuelo.org/","http://arborea.io","http://www.coloradd.net/","http://www.discovering-hands.de/en/","http://givevision.net/",
        #           "http://www.kaitiaki.it/en/","https://www.magikme.net/","https://www.mycarematters.org/","https://www.refugeeswork.at/","https://www.freebirdclub.com/",
        #           "http://www.ultraspecialisti.com/","https://www.walkwithpath.com/","http://www.iosmosi.com/en/",
        #           "https://www.edukit.org.uk/","https://sharingacademy.com/en","http://www.silentsecret.com","http://www.aprendicesvisuales.org/en/","http://www.biocarbonengineering.com",
        #           "http://www.lazzus.com/","http://www.desolenator.com/","https://www.mycarematters.org/","http://ithacalaundry.gr/en/","http://www.fitforkids.dk/en/",
        #           "https://www.feelif.com/","https://www.bgood.at/","http://blitab.com/","http://www.designbypana.com/","https://www.ecosia.org/",
        #           "http://www.fitforkids.dk/en/","http://www.koiki.eu/en/","http://www.letsgetsporty.com/","http://www.marioway.it/word/en",
        #           "http://peppypals.com/","https://bluebadgestyle.com/","https://www.adie.org/microfinance-in-france","http://www.clear-village.org","https://thedoschool.org/",
        #           "http://helioz.org","https://www.mattecentrum.se","http://www.1toit2ages.be/en/","http://www.bikway.com/",
        #           "https://buuv.nu/info/english","http://organery.co/","http://www.ortialti.com/en/","https://theyardtheatre.co.uk/",
        #           "http://bincome.eu/","https://bc4gd.com/","https://wikihouse.cc/","https://collaction.org/","https://cultivai.com/","http://www.thirdageireland.ie/",
        #           "https://www.feelif.com/","https://www.leapslab.com/","http://www.inclu-sight.com/","https://fightthestroke.org/en/","http://www.dialogue-se.com/",
        #           "http://mouse4all.com/en/","http://www.openbiomedical.org/","https://www.scribeasy.com/","https://saga.one/","http://siboxapp.com/en/",
        #           "https://www.signly.co/","http://solomon.gr/","http://www.barrabes.biz/en/","https://www.wayfindr.net/","http://action.neweconomics.org/",
        #           "https://www.cucula.org/","http://www.themachinetobeanother.org/","https://aid.technology/","https://www.micro-rainbow.org/","https://www.solidaritysalt.com/",
        #           "http://thebikeproject.co.uk/","http://www.adamantbionrg.com/","https://habibi.at/en/","http://www.mygrantour.org/en/","http://coreorient.com/en/",
        #           "https://www.refugeeswork.at/","http://www.learningunlimited.co/","https://wedocare.dei.uc.pt/","https://www.thefreebirdclub.com/","https://www.wheeliz.com/en",
        #           "http://melawear.de/en/","http://jakodoma.org/english/","http://www.ssmsapp.com/","http://www.galiboff.com/","http://www.roda.hr/en",
        #           "http://instituteintercer.org/en","http://www.loveyourwaste.com/english/","https://crowdfundhq.com/","http://www.cfmitalia.it/english/","http://www.tasksquadhq.com/",
        #           "http://www.hazelheartwood.com/","http://theurbanfarmer.co/","https://www.happyfeetpreschool.net/","http://www.scn.org/","https://www.ipn.pt/","http://grc.engineering.cf.ac.uk/",
        #           "https://www.science-link.eu/","http://www.biobasenwe.org/en/","http://www.innove.ee/en","http://www.greenpolis.fi/en/",
        #           "http://seap-alps.eu/hp2/Home.htm","https://www.cteg.org.uk/","http://www.eoi.es/portal/en","https://mka.malopolska.pl/en/strona-glowna",
        #           "https://www.olsztyn.eu/en/","http://exeko.org/en","http://www.rdsp.com/","http://www.rootsofempathy.org/","http://janeswalk.org/",
        #           "https://www.jumpmath.org/","https://www.simprints.com/","http://hippogriff.se/"
                  ]
    rules = [Rule(LinkExtractor(allow=".*"), callback="parse_start_url", follow=True)]

    # def __init__(self, crawl_pages=True, moreparams=None, *args, **kwargs):
    #     super(EIBCompetitionspider, self).__init__(*args, **kwargs)
    #     # Set the class member from here
    #     if (crawl_pages is True):
    #         regs = []
    #         for dom in  self.start_urls:
    #             regs.append(dom+".*")#http://www.openbiomedical.org/obmstory/
    #         EIBCompetitionspider.rules = (Rule(LinkExtractor(allow=".*"), callback="parse_start_url", follow=True),)
    #
    #         super(EIBCompetitionspider, self)._compile_rules()
    #     self.moreparams = moreparams




    def parse_start_url(self, response):
        source_page = response.url
        print source_page
        if "facebook.com" in source_page or "vk.com" in source_page or "youtube.com" in source_page or "twitter.com" in source_page or \
                        "linkedin" in source_page or "vimeo" in source_page or "instagram" in source_page or "google" in source_page or "github" in source_page \
                or "pinterest" in source_page:
            return

        all_page_links = response.xpath('//a/@href').extract()
        item = SIScrapedItem()
        item.URL = source_page
        try:
            ptitle = response.xpath('//title').extract()
            if len(ptitle) > 0:
                item.PageTitle = strip_tags(response.xpath('//title').extract()[0])
            else:
                item.PageTitle = ""
        except Exception as ex:
            print ex.message

        parsed_uri = "--"
        try:
            item.Content = unicode(response.body, "utf-8", errors='replace')
            s = fromstring(response.body)
            cleaner = Cleaner()
            cleaner.javascript = True  # This is True because we want to activate the javascript filter
            cleaner.style = True
            s2 = cleaner.clean_html(s)
            inner_html = tostring(s2)

            item.Text = strip_tags(inner_html)
            parsed_uri = urlparse(item.URL)
        except Exception as ex:
            print ex.message
            return
        domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
        client = MongoClient()
        db = client.ESID
        domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
        result = db.EIBCompetition8.insert_one(
            {
                "domain":domain,
                "name": item.Name,
                "url": item.URL,
                "page_title": item.PageTitle,
                "content": item.Content,
                "text": str(item.Text)
            }

        )

        yield item