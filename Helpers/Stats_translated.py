#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import MySQLdb
from database_access import *
import smtplib
from q_email import *
import datetime


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
    number_of_projects_with_less_then_500char = db.crawl20180801_translated.find({"translationLen": {"$lt": 500}}).count()
    #############################################################
    # number_of_projects_between_500_1000 = 0
    number_of_projects_between_500_1000 = db.crawl20180801_translated.find({"translationLen": {"$gt":500,"$lt": 1000}}).count()
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
    number_of_projects_desc_smaller_500 = db.crawl20180801_translated.find({"DescriptionLength": {"$lt": 500}}).count()
    # number_of_projects_desc_between_500_1000 = 0
    number_of_projects_desc_between_500_1000 = db.crawl20180801_translated.find({"DescriptionLength": {"$gt": 500,"$lt":1000}}).count()
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
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 500}})
    for pro in everything:
        sql = "Select count(*) from ProjectLocation where Projects_idProjects={0} and Country is not null and Country <>''".format(pro['mysql_databaseID'])
        cursor.execute(sql)
        results = cursor.fetchall()
        if results[0][0]>0:
            number_of_projects_with_usable_info_having_country = number_of_projects_with_usable_info_having_country + 1
    # number_of_projects_with_usable_info_having_city = 0
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 500}})
    for pro in everything:
        sql = "Select count(*) from ProjectLocation where Projects_idProjects={0} and City is not null and City <>''".format(
            pro['mysql_databaseID'])
        cursor.execute(sql)
        results = cursor.fetchall()
        if results[0][0] > 0:
            number_of_projects_with_usable_info_having_city = number_of_projects_with_usable_info_having_city + 1
        # number_of_projects_with_usable_info_having_linked_actor = 0
    everything = db.crawl20180801_translated.find({"translationLen": {"$gt": 500}})
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
    everything = db.crawl20180801_translated.find({"translationLen":{"$gt":500}})
    for pro in everything:
        sql = "Select * from AdditionalProjectData where FieldName like '%Desc%' and Value is not Null and Value <>'' and Projects_idProjects="+pro['mysql_databaseID']
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)>0:
            num_proj_w_desc = num_proj_w_desc + 1
    #####################################################################
    langstr = ""
    for l in languages:
        langstr = langstr+l+":"+str(languages[l])+"\r\n"
    actors_str = ""
    for actors in project_actors:
        actors_str = actors_str+actors+": "+str(project_actors[actors])+"\r\n"
    sources_str = ""
    for sources in sources_projects:
        sources_str = sources_str + sources + ": " + str(sources_projects[sources]) + "\r\n"
    actors_s_str = ""
    for sources in sources_actors:
        actors_s_str = actors_s_str + sources + ": " + str(sources_actors[sources]) + "\r\n"

    sent_from = 'nikola.milosevic86@gmail.com'
    to = ['nikola.milosevic@manchester.ac.uk']
    x = datetime.datetime.now()
    subject = 'ESID Report for '+str(x)
    body = """Hello, \n\n
Here is the report of newest statistics from European Social Innovation database, created on {0}.
    
Number of projects: {1}
Number of projects with website: {2}
Number of projects with description: {3} \n
Number of projects with website and description: {4} \n
Number of projects with no website and no description {5}\n
------------------------------------------------------------
Number of projects crawled: {6} \r\n
Crawled from social media (Facebook, Google (including android store), Twitter, Youtube): {7}\r\n
Number of projects with translations (description + web): {8}\r\n
Number of projects with translations shorter then 500 characters: {9}\r\n
Number of projects with translations shorter then 1000 characters and longer then 500: {10}\r\n
Number of projects with translations shorter then 10,000 characters and longer then 1000: {11}\r\n
Number of projects with translations shorter then 100,000 characters and longer then 10,000: {12}\r\n
Number of projects with translations longer then 100,000: {13}\r\n
Number of projects with description and no webpage: {14}\r\n
Number of projects having description shorter then 500 chars: {15}\r\n
Number of projects having description between 500-1000 chars: {16}\r\n
Number of projects having description between 1000-10,000 chars: {17}\r\n
Number of projects having description between 10,000-100,000 chars: {18}\r\n
Number of projects having description longer then 100,000 chars: {19}\r\n
Languages:\r\n
{20}\r\n

Number of projects having usable amount of text also having country: {21}\r\n
Number of projects having usable amount of text also having city: {22}\r\n
Number of projects having usable amount of text also having actor: {23}\r\n
Projects having linked actors by datasource: 
{24}\r\n
Number of actors: {25}\r\n
Number of actors with websites: {26}\r\n
Number of actors linked to a project: {27}\r\n
Project sources:\r\n
{28}\r\n
Actor sources:\r\n
{29}\r\n

    
    \n\n Best wishes \n ESID Team""".format(str(x),str(number_of_projects),str(number_of_projects_with_website),
str(number_of_projects_with_desc),str(number_of_projects_with_web_and_desc),str(number_of_projects_no_web_no_desc),str(number_of_crawled),
str(crawled_social_media),str(number_of_projects_with_translations),str(number_of_projects_with_less_then_500char),str(number_of_projects_between_500_1000),
str(number_of_projects_between_1000_1000),str(number_of_projects_between_10000_100000),str(number_of_projects_larger_100000),
str(number_of_projects_with_desc_no_web),str(number_of_projects_desc_smaller_500),str(number_of_projects_desc_between_500_1000),
str(number_of_projects_desc_between_1000_10000),str(number_of_projects_desc_between_10000_100000),str(number_of_projects_desc_larger_100000),
str(langstr),str(number_of_projects_with_usable_info_having_country),str(number_of_projects_with_usable_info_having_city),str(number_of_projects_with_usable_info_having_linked_actor),
str(actors_str),str(number_of_actors),str(number_of_actors_with_web),str(number_of_actors_linked_to_project),str(sources_str),str(actors_s_str)

                                            )
    msg = "\r\n".join([
        "From: ESID Database (eusidatabase@gmail.com)",
        "To: nikola.milosevic@manchester.ac.uk, abdullah.gok@strath.ac.uk",
        "Subject: "+subject,
        "",
        body
    ])
    server.sendmail("eusidatabase@gmail.com", ["nikola.milosevic@manchester.ac.uk","abdullah.gok@strath.ac.uk"], msg)
    server.close()

