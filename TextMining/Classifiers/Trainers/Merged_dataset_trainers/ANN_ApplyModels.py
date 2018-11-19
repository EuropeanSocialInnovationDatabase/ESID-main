# -*- coding: utf-8 -*-
from pymongo import MongoClient
from ANN_Experiments import UniversalNNClassifier
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
    objective_cls = UniversalNNClassifier()
    objective_cls.load_CNN_model("Objectives_LSTM")
    actors_cls = UniversalNNClassifier()
    actors_cls.load_CNN_model("Actors_LSTM")
    outputs_cls = UniversalNNClassifier()
    outputs_cls.load_CNN_model("Outputs_LSTM")
    innovativeness_cls = UniversalNNClassifier()
    innovativeness_cls.load_CNN_model("Innovativeness_LSTM")
    for res in results:
        print res[0]
        message = ""
        option = "v19 CNN+LSTM 200d embeddings unbalanced, 15/11/2018"
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
        elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower()\
                or "abbiamo appena registrato" in document_text.lower() or "neither the service provider nor the domain owner maintain any relationship with the advertisers." in document_text.lower()\
                or "to purchase, call buydomains" in document_text.lower() or "hundreds of thousands of premium domains" in document_text.lower() or "search for a premium domain" in document_text.lower()\
                or "This domain is registered for one" in document_text.lower() or "for your website name!" in document_text.lower():
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
            objective = objective_cls.predict_CNN([document_text])[0]
            actors = actors_cls.predict_CNN([document_text])[0]
            outputs = outputs_cls.predict_CNN([document_text])[0]
            innovativeness = innovativeness_cls.predict_CNN([document_text])[0]
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            mysql_cursor.execute(sql)
            db_mysql.commit()
    print("Done!")