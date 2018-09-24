#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pymongo import MongoClient
import MySQLdb
from database_access import *
import smtplib
from q_email import *
import datetime
from MakePerProjectStats import make_stats_csv


if __name__ == '__main__':
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_email, my_password)
    client = MongoClient()
    db = client.ESID
    dba = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = dba.cursor()
    number_of_projects = 0
    number_of_projects_with_website = 0
    number_of_projects_with_desc = 0
    number_of_projects_with_web_and_desc = 0
    number_of_projects_no_web_no_desc =0
    number_of_crawled = 0
    crawled_social_media = 0
    number_of_projects_with_translations = 0
    number_of_projects_with_less_then_500char = 0
    number_of_projects_between_500_1000 = 0
    number_of_projects_between_1000_1000 = 0
    number_of_projects_between_10000_100000 = 0
    number_of_projects_larger_100000 = 0
    number_of_projects_with_desc_no_web = 0
    number_of_projects_desc_smaller_500 = 0
    number_of_projects_desc_between_500_1000 = 0
    number_of_projects_desc_between_1000_10000 = 0
    number_of_projects_desc_between_10000_100000 = 0
    number_of_projects_desc_larger_100000 = 0
    #number_of_projects_with_min_usable_info = 0
    languages = {}
    number_of_projects_with_usable_info_having_country = 0
    number_of_projects_with_usable_info_having_city = 0
    number_of_projects_with_usable_info_having_linked_actor = 0
    number_of_projects_with_usable_info_having_desc = 0
    projects_having_country = 0
    projects_having_city = 0
    projects_having_actor = 0
    number_of_actors = 0
    number_of_actors_with_web = 0
    number_of_actors_linked_to_project = 0
    sources_projects = {}
    sources_actors = {}
    make_stats_csv()

    num_proj_w_desc = 0
    # Number of Projects
    sql = "Select count(*) from Projects where Exclude=0"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects = res[0]
    #####################################################
    # Number of projects with website
    sql = "Select count(*) from Projects where Exclude=0 and ProjectWebpage is not null and ProjectWebpage<>''"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects_with_website = res[0]
    # Number of projects with description
    sql = "SELECT count(distinct(Projects_idProjects)) FROM EDSI.AdditionalProjectData inner join Projects on idProjects=Projects_idProjects where FieldName like '%Desc%' and Value<>'' and Exclude = 0"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects_with_desc = res[0]
    ##########################################################
    #number_of_projects_with_web_and_desc
    sql = "SELECT count(distinct(Projects_idProjects)) FROM EDSI.AdditionalProjectData inner join Projects on idProjects=Projects_idProjects where FieldName like '%Desc%' and Value<>'' and Exclude = 0 and ProjectWebpage is not null and ProjectWebpage<>''"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects_with_web_and_desc = res[0]
    ##########################################################
    #number_of_projects_no_web_no_desc
    sql = "SELECT count(distinct(Projects_idProjects)) FROM EDSI.AdditionalProjectData inner join Projects on idProjects=Projects_idProjects where FieldName not like '%Desc%' and Exclude = 0 and (ProjectWebpage is null or ProjectWebpage='');"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects_no_web_no_desc = res[0]
    ###############################################################
    # number_of_crawled
    number_of_crawled = len(db.crawl20180801.distinct('mysql_databaseID'))
    #############################################################
    # crawled_social_media
    sql = "Select count(*) from Projects where Exclude=0 and (ProjectWebpage like '%facebook%' or ProjectWebpage like '%google%' or ProjectWebpage like '%youtube%' or ProjectWebpage like '%twitter%') "
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        crawled_social_media = res[0]
    ############################################################
    # number_of_projects_with_translations
    number_of_projects_with_translations = len(db.crawl20180801_translated.distinct('mysql_databaseID'))
    ############################################################
    #number_of_projects_with_less_then_500char
    number_of_projects_with_less_then_500char = db.crawl20180801_translated.find({"translationLen": {"$lt": 350}}).count()
    #############################################################
    # number_of_projects_between_500_1000 = 0
    number_of_projects_between_500_1000 = db.crawl20180801_translated.find({"translationLen": {"$gt":350,"$lt": 1000}}).count()
    # number_of_projects_between_1000_1000 = 0
    number_of_projects_between_1000_1000 = db.crawl20180801_translated.find({"translationLen": {"$gt": 1000, "$lt": 10000}}).count()
    # number_of_projects_between_10000_100000 = 0
    number_of_projects_between_10000_100000 = db.crawl20180801_translated.find({"translationLen": {"$gt": 10000, "$lt": 100000}}).count()
    #'number_of_projects_larger_100000 = 0'
    number_of_projects_larger_100000 = db.crawl20180801_translated.find({"translationLen": { "$gt": 100000}}).count()
    #number_of_projects_with_desc_no_web
    sql = "SELECT count(distinct(Projects_idProjects)) FROM EDSI.AdditionalProjectData inner join Projects on idProjects=Projects_idProjects where FieldName like '%Desc%' and Value<>'' and Exclude = 0 and (ProjectWebpage is null or ProjectWebpage='')"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_projects_with_desc_no_web = res[0]
    # number_of_projects_desc_smaller_500 = 0
    number_of_projects_desc_smaller_500 = db.crawl20180801_translated.find({"DescriptionLength": {"$lt": 350}}).count()
    # number_of_projects_desc_between_500_1000 = 0
    number_of_projects_desc_between_500_1000 = db.crawl20180801_translated.find({"DescriptionLength": {"$gt": 350,"$lt":1000}}).count()
    # number_of_projects_desc_between_1000_10000 = 0
    number_of_projects_desc_between_1000_10000 = db.crawl20180801_translated.find({"DescriptionLength": {"$gt": 1000, "$lt": 10000}}).count()
    # number_of_projects_desc_between_10000_100000 = 0
    number_of_projects_desc_between_10000_100000 = db.crawl20180801_translated.find({"DescriptionLength": {"$gt": 10000, "$lt": 100000}}).count()
    # number_of_projects_desc_larger_100000 = 0
    number_of_projects_desc_larger_100000 =db.crawl20180801_translated.find({"DescriptionLength": {"$gt": 100000}}).count()


    everything = db.crawl20180801_translated.find({})
    for pro in everything:
        if pro['Language'] not in languages.keys():
            languages[pro['Language']] = 1
        else:
            languages[pro['Language']] = languages[pro['Language']] + 1
        # number_of_projects_with_usable_info_having_country = 0
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 350}})
    for pro in everything:
        sql = "Select count(*) from ProjectLocation where Projects_idProjects={0} and Country is not null and Country <>''".format(pro['mysql_databaseID'])
        cursor.execute(sql)
        results = cursor.fetchall()
        if results[0][0]>0:
            number_of_projects_with_usable_info_having_country = number_of_projects_with_usable_info_having_country + 1
    # number_of_projects_with_usable_info_having_city = 0
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 350}})
    for pro in everything:
        sql = "Select count(*) from ProjectLocation where Projects_idProjects={0} and City is not null and City <>''".format(
            pro['mysql_databaseID'])
        cursor.execute(sql)
        results = cursor.fetchall()
        if results[0][0] > 0:
            number_of_projects_with_usable_info_having_city = number_of_projects_with_usable_info_having_city + 1
        # number_of_projects_with_usable_info_having_linked_actor = 0
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 350}})
    for pro in everything:
        sql = "Select count(*) from Actors_has_Projects where Projects_idProjects={0}".format(
            pro['mysql_databaseID'])
        cursor.execute(sql)
        results = cursor.fetchall()
        if results[0][0] > 0:
            number_of_projects_with_usable_info_having_linked_actor = number_of_projects_with_usable_info_having_linked_actor + 1
        # number_of_projects_with_usable_info_having_desc = 0
    # projects_having_country = 0
    sql = "SELECT count(distinct(idProjects)) FROM Projects left join EDSI.ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and Country is not null and Country<>''"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        projects_having_country = res[0]

        # projects_having_city = 0
    sql = "SELECT count(distinct(idProjects)) FROM Projects left join EDSI.ProjectLocation on idProjects=Projects_idProjects where Exclude = 0 and City is not null and City<>''"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        projects_having_city = res[0]
        # projects_having_actor = 0
    project_actors = {}
    sql = "SELECT FirstDataSource,count(distinct(idProjects)) as cnt  FROM Projects inner join Actors_has_Projects on idProjects=Projects_idProjects where Exclude = 0 group by FirstDataSource order by cnt desc"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        project_actors[res[0]]=res[1]

        # number_of_actors = 0
    sql = "SELECT count(distinct(idActors)) FROM Actors"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_actors = res[0]
        # number_of_actors_with_web = 0
    sql = "SELECT count(distinct(idActors)) FROM Actors where ActorWebsite is not null and ActorWebsite<>''"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_actors_with_web = res[0]
        # number_of_actors_linked_to_project = 0
    sql = "SELECT count(distinct(Actors_idActors)) FROM EDSI.Actors_has_Projects inner join Projects on idProjects = Projects_idProjects where Exclude =0;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        number_of_actors_linked_to_project = res[0]
    # sources_projects = {}
    sql = "SELECT FirstDataSource,count(distinct(idProjects)) as cnt FROM EDSI.Projects where Exclude = 0 group by FirstDataSource order by cnt desc;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        sources_projects[res[0]] = res[1]
    # sources_actors = {}
    sql = "SELECT SourceOriginallyObtained,count(distinct(idActors)) as cnt FROM EDSI.Actors group by SourceOriginallyObtained order by cnt desc;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        if res[0] is not None:
            sources_actors[res[0]] = res[1]
        else:
            sources_actors["Others"] = res[1]
    # Number of projects with descriptions
    everything = db.crawl20180801_translated.find({"translationLen":{"$gt":350}})
    for pro in everything:
        sql = "Select * from AdditionalProjectData where FieldName like '%Desc%' and Value is not Null and Value <>'' and Projects_idProjects="+pro['mysql_databaseID']
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)>0:
            num_proj_w_desc = num_proj_w_desc + 1
    #####################################################################
    langstr = "<table>"
    for l in languages:
        langstr = langstr+"<tr><td>"+l+":</td><td>"+str(languages[l])+"</td></tr>\r\n"
    langstr = langstr+"</table>"
    actors_str = "<table>"
    for actors in project_actors:
        actors_str = actors_str+"<tr><td>"+actors+":</td><td>"+str(project_actors[actors])+"</td></tr>\r\n"
    actors_str = actors_str+'</table>'
    sources_str = "<table>"
    for sources in sources_projects:
        sources_str = sources_str+"<tr><td>"+sources + ":</td><td> " + str(sources_projects[sources]) + "</td></tr>\r\n"
    sources_str = sources_str +'</table>'
    actors_s_str = "<table>"
    for sources in sources_actors:
        actors_s_str = actors_s_str +"<tr><td>"+ sources + ":</td><td> "  + str(sources_actors[sources]) + "</td></tr>\r\n"
    actors_s_str = actors_s_str +'</table>'

    sent_from = 'nikola.milosevic86@gmail.com'
    to = ['nikola.milosevic@manchester.ac.uk']
    x = datetime.datetime.now()
    subject = 'ESID Report for '+str(x)
    body = """Hello, \n\n<br/><br/>
Here is the report of newest statistics from European Social Innovation database, created on {0}.<br/><br/>

<table>    
<tr><td>Number of projects: </td><td>{1} </td></tr>
<tr><td>Number of projects with website: </td><td>{2} </td></tr>\n
<tr><td>Number of projects with description: </td><td>{3} </td></tr>\n
<tr><td>Number of projects with website and description: </td><td>{4}</td></tr> \n
<tr><td>Number of projects with no website and no description </td><td>{5}</td></tr>\n
<tr><td></td><td></td></tr>
<tr><td>Number of projects crawled:</td><td> {6} </td></tr>\r\n
<tr><td>Crawled from social media (Facebook, Google (including android store), Twitter, Youtube): </td><td>{7}</td></tr>\r\n
<tr><td>Number of projects with translations (description + web):</td><td> {8}</td></tr>\r\n
<tr><td>Number of projects with translations shorter then 350 characters: </td><td>{9}</td></tr>\r\n
<tr><td>Number of projects with translations shorter then 1000 characters and longer then 350: </td><td>{10}</td></tr>\r\n
<tr><td>Number of projects with translations shorter then 10,000 characters and longer then 1000:</td><td> {11}</td></tr>\r\n
<tr><td>Number of projects with translations shorter then 100,000 characters and longer then 10,000:</td><td> {12}</td></tr>\r\n
<tr><td>Number of projects with translations longer then 100,000:</td><td> {13}</td></tr>\r\n
<tr><td>Number of projects with description and no webpage: </td><td>{14}</td></tr>\r\n
<tr><td>Number of projects having description shorter then 350 chars: </td><td>{15}</td></tr>\r\n
<tr><td>Number of projects having description between 350-1000 chars:</td><td> {16}</td></tr>\r\n
<tr><td>Number of projects having description between 1000-10,000 chars: </td><td>{17}</td></tr>\r\n
<tr><td>Number of projects having description between 10,000-100,000 chars: </td><td>{18}</td></tr>\r\n
<tr><td>Number of projects having description longer then 100,000 chars: </td><td>{19}</td></tr>\r\n
<tr><td>Languages:\r\n</td><td></td></tr>
<tr><td>{20}\r\n</td><td></td></tr>

<tr><td>Number of projects having usable amount of text also having country: </td><td>{21}</td></tr>\r\n
<tr><td>Number of projects having usable amount of text also having city: </td><td>{22}</td></tr>\r\n
<tr><td>Number of projects having usable amount of text also having actor: </td><td>{23}</td></tr>\r\n
<tr><td>Projects having linked actors by datasource: </td><td></td></tr>
<tr><td>{24}\r\n</td><td></td></tr>
<tr><td>Number of actors:</td><td> {25}</td></tr>\r\n
<tr><td>Number of actors with websites:</td><td> {26}</td></tr>\r\n
<tr><td>Number of actors linked to a project:</td><td> {27}</td></tr>\r\n
<tr><td>Project sources:\r\n</td><td></td></tr>
<tr><td>{28}\r\n</td><td></td></tr>
<tr><td>Actor sources:\r\n</td><td></td></tr>
<tr><td>{29}\r\n</td><td></td></tr>
</table>
<br/><br/>
    
    \n\n Best wishes <br/>\n ESID Team""".format(str(x),str(number_of_projects),str(number_of_projects_with_website),
str(number_of_projects_with_desc),str(number_of_projects_with_web_and_desc),str(number_of_projects_no_web_no_desc),str(number_of_crawled),
str(crawled_social_media),str(number_of_projects_with_translations),str(number_of_projects_with_less_then_500char),str(number_of_projects_between_500_1000),
str(number_of_projects_between_1000_1000),str(number_of_projects_between_10000_100000),str(number_of_projects_larger_100000),
str(number_of_projects_with_desc_no_web),str(number_of_projects_desc_smaller_500),str(number_of_projects_desc_between_500_1000),
str(number_of_projects_desc_between_1000_10000),str(number_of_projects_desc_between_10000_100000),str(number_of_projects_desc_larger_100000),
str(langstr),str(number_of_projects_with_usable_info_having_country),str(number_of_projects_with_usable_info_having_city),str(number_of_projects_with_usable_info_having_linked_actor),
str(actors_str),str(number_of_actors),str(number_of_actors_with_web),str(number_of_actors_linked_to_project),str(sources_str),str(actors_s_str)

                                            )

    msg = MIMEMultipart('alternative')
    msg['From'] = "ESID Database (eusidatabase@gmail.com)"
    msg['To'] = "nikola.milosevic@manchester.ac.uk,abdullah.gok@strath.ac.uk"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    msg.attach(MIMEText(body, 'plain'))

    filename = "project_stats.csv"
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)


    # msg = "\r\n".join([
    #     "From: ESID Database (eusidatabase@gmail.com)",
    #     "To: nikola.milosevic@manchester.ac.uk",
    #     "Subject: "+subject,
    #     "",
    #     body
    # ])
    text = msg.as_string()
    server.sendmail("eusidatabase@gmail.com", ["nikola.milosevic@manchester.ac.uk","abdullah.gok@strath.ac.uk","gnenadic@manchester.ac.uk"], text)
    server.close()

