# -*- coding: utf-8 -*-
from pymongo import MongoClient
from Basic_experiments import UniversalClassifier
import MySQLdb
from database_access import *

if  __name__ == '__main__':
    wayback_bar = """ <![endif]   BEGIN WAYBACK TOOLBAR INSERT   success  fail   NEXT/PREV MONTH NAV AND MONTH INDICATOR   Oct  MAY  Jun   NEXT/PREV CAPTURE NAV AND DAY OF MONTH INDICATOR   14   NEXT/PREV YEAR NAV AND YEAR INDICATOR"""
    wayback_bar2 = """About this capture  COLLECTED BY  		Organization:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  Collection:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  TIMESTAMPS   END WAYBACK TOOLBAR INSERT   [if lt IE 7]><p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p><![endif]"""
    db_mysql = MySQLdb.connect(host, username, password, database, charset='utf8')
    mysql_cursor = db_mysql.cursor()
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    sql = "Select * from Projects where Exclude =0"
    mysql_cursor.execute(sql)
    results = mysql_cursor.fetchall()
    objective_cls = UniversalClassifier()
    objective_cls.load_RF_words_only("Objectives_RF")
    actors_cls = UniversalClassifier()
    actors_cls.load_RF_words_only("Actors_RF")
    outputs_cls = UniversalClassifier()
    outputs_cls.load_RF_words_only("Outputs_RF")
    innovativeness_cls = UniversalClassifier()
    innovativeness_cls.load_RF_words_only("Innovativeness_RF")
    for res in results:
        print res[0]
        message = ""
        option = "v6 classifier with excluded as balancing, 04/10/2018"
        objective = 0
        actors = 0
        outputs = 0
        innovativeness = 0
        project_id = res[0]
        documents = mongo_db.crawl20180801_translated.find({"mysql_databaseID": str(project_id)},
                                                no_cursor_timeout=True).batch_size(100)
        document_text = ""
        for doc in documents:
            document_text = document_text+doc['translation']
        if len(document_text)<350 or "domain sale" in document_text:
            documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)},
                                                    no_cursor_timeout=True).batch_size(100)
            document_text = ""
            for doc in documents2:
                document_text = document_text + " "+doc['translation']
        if "404" in document_text or "page not found" in document_text.lower():
            message = "Page not found"
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective,actors,outputs,innovativeness,project_id,option,message)
            mysql_cursor.execute(sql)
            db_mysql.commit()
        elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower():
            message = "Domain for sale"
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            mysql_cursor.execute(sql)
            db_mysql.commit()
        elif len(document_text)<350:
            message = "Text smaller than 350 characters"
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            mysql_cursor.execute(sql)
            db_mysql.commit()
        else:
            objective = objective_cls.predict_words_only([document_text])[0]
            actors = actors_cls.predict_words_only([document_text])[0]
            outputs = outputs_cls.predict_words_only([document_text])[0]
            innovativeness = innovativeness_cls.predict_words_only([document_text])[0]
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            mysql_cursor.execute(sql)
            db_mysql.commit()
    print("Done!")