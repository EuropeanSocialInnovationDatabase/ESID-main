
from HTMLParser import HTMLParser
from StringIO import StringIO

import scrapy
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from scrapy.linkextractors import LinkExtractor
import re
import BeautifulSoup
import time
from scrapy.spiders import Rule, CrawlSpider
from urlparse import urlparse
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


def pdfparser(data):

    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data = retstr.getvalue()

    return data

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


class GeneralWebsiteRulespiderWayback(CrawlSpider):
    name = "WaybackIndividualSpider"
    allowed_domains = []
    start_urls = []
    dataType = ''
    MySQLID = ''
    Name = ''

    def __init__(self, crawl_pages=True, moreparams=None,url='',type="Project",id='',Name ="", *args, **kwargs):
        super(GeneralWebsiteRulespiderWayback, self).__init__(*args, **kwargs)
        # Set the GeneralWebsiteRulespider member from here
        if (crawl_pages is True):
            self.MySQLID = id
            self.dataType = type
            self.Name = Name
            # Then recompile the Rules
            parsed_uri = urlparse(url)
            domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
            self.allowed_domains.append(domain)

            self.start_urls.append(url)
            regs = []
            for dom in  self.start_urls:
                regs.append(dom+".*")
            GeneralWebsiteRulespiderWayback.rules = (Rule(LinkExtractor(allow=regs), callback="parse_start_url", follow=True),)

            super(GeneralWebsiteRulespiderWayback, self)._compile_rules()
        self.moreparams = moreparams


    def parse_start_url(self, response):
        source_page = response.url
        actorWeb = ""
        ProWeb = ""
        if self.dataType=="Project":
            ProWeb = self.start_urls[0]
        else:
            actorWeb = self.start_urls[0]
        print source_page
        if "facebook.com" in source_page or "vk.com" in source_page or "youtube.com" in source_page or "twitter.com" in source_page or \
                        "linkedin" in source_page or "vimeo" in source_page or "instagram" in source_page or "google" in source_page \
                or "pinterest" in source_page:
            return

        all_page_links = response.xpath('//a/@href').extract()
        item = SIScrapedItem()
        item.URL = source_page
        if ".pdf" in source_page:
            pdf = response.body
            output = file("temp.pdf", 'wb')
            output.write(pdf)
            output.close()
            item.Content = pdfparser("temp.pdf")
        else:
            ptitle = response.xpath('//title').extract()
            if len(ptitle)>0:
                item.PageTitle = strip_tags(response.xpath('//title').extract()[0])
            else:
                item.PageTitle = ""
            item.Content = response.body
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
            item.Text = content.replace("&nbsp;"," ")

        parsed_uri = urlparse(item.URL)
        domain = '{uri.netloc}/'.format(uri=parsed_uri).replace("/", "").replace("www.", "")
        #edit_distance = nltk.edit_distance(source_page, ProWeb)
        # Why is this here?
        # To prevent too different sites to be crawled
        if ProWeb != source_page and ProWeb not in source_page and ProWeb.replace("http:","https:") != source_page and actorWeb != source_page and domain != actorWeb and domain != ProWeb and \
                                "http://"+domain != actorWeb and "http://"+domain + "/" != actorWeb and \
                                "http://www."+domain != actorWeb and "http://www."+domain + "/"!= actorWeb and \
                                "https://"+domain != actorWeb and "https://"+domain + "/" != actorWeb and \
                                "https://www."+domain != actorWeb and "https://www."+domain +"/"!= actorWeb  and \
                                "http://" + domain != ProWeb and "http://" + domain + "/" != ProWeb and "http://www." + domain != ProWeb and \
                                "https://" + domain != ProWeb and "https://www." + domain != ProWeb:
            print "Returning: "+domain+"   "+source_page+"    "+actorWeb+"    "+ProWeb
            return
        item.DatabaseID = self.MySQLID
        item.RelatedTo = self.dataType
        item.Name = self.Name
        if(item.DatabaseID == None or item.DatabaseID==""):
            return
        client = MongoClient()
        db = client.ESID

        result = db.crawl20180801_wayback.insert_one(
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