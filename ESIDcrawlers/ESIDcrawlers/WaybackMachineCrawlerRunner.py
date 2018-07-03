#!/usr/bin/env python
import MySQLdb
# from scrapy.crawler import CrawlerProcess, Crawler
import os
import subprocess
import requests
import json

# from ESIDcrawlers.ESIDcrawlers.spiders import IndividualSpider
from database_access import *

#subprocess.check_output(['ls','-l']) #all that is technically needed...
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql = "Select idProjects,ProjectName,ProjectWebpage from Projects where InactiveWebsite = 1"
cursor.execute(sql)
results = cursor.fetchall()
number_of_err = 0
number_crawled = 0

for res in results:
    try:
        url = res[2]
        r = requests.get('http://archive.org/wayback/available?url='+url)
        json_text = r.json()
        new_url = json_text["archived_snapshots"]["closest"]["url"]

        command = 'scrapy crawl WaybackIndividualSpider -a '+str('url='+new_url.encode('utf-8'))+' -a'+' id='+str(res[0])+' -a'+ str(' Name="'+str(res[1].encode('utf-8'))+'"')
        os.system(command)
        number_crawled = number_crawled + 1

    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    except Exception as e1:
        print "Exception in json"
        number_of_err = number_of_err + 1

print("Number of missing sites on Wayback machine "+str(number_of_err))
print("Number of crawled sites on Wayback machine "+str(number_crawled))


