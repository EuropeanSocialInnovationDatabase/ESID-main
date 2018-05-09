#!/usr/bin/env python
import MySQLdb
# from scrapy.crawler import CrawlerProcess, Crawler
import os
import subprocess

# from ESIDcrawlers.ESIDcrawlers.spiders import IndividualSpider
from database_access import *

#subprocess.check_output(['ls','-l']) #all that is technically needed...
db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()
sql = "Select idProjects,ProjectName,ProjectWebpage from Projects"
cursor.execute(sql)
results = cursor.fetchall()
try:
    for res in results:
        if res[2] == None:
            continue

        command = 'scrapy crawl IndividualSpider -a '+str('url='+res[2].encode('utf-8'))+' -a'+' id='+str(res[0])+' -a'+ str(' Name="'+str(res[1].encode('utf-8'))+'"')
        #subprocess.call(command,shell=True)
        os.system(command)
        #subprocess.call(command)
        # setting = get_project_settings()
        # crawler = Crawler(setting)
        # spider = IndividualSpider(Name=res[1],id=res[0],url=res[2])
        # crawler.configure()
        # crawler.crawl(spider)
        # crawler.start()
        # process = CrawlerProcess()
        # arglist = ["Name="+res[1],"url="+res[2],"id="+str(res[0])]
        # process.crawl(IndividualSpider,arglist)
        # process.start()
        #print subprocess.check_call(['ls','-la'])
        #print subprocess.check_call(['scrapy','crawl', 'IndividualSpider', '-a', str('url='+res[2]), '-a', 'id='+str(res[0]),'-a', str('Name='+res[1])],shell=True)
except subprocess.CalledProcessError as e:
    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


