# -*- coding: utf-8 -*-
from pymongo import MongoClient
from Basic_experiments import UniversalClassifier
import MySQLdb
from database_access import *
from langdetect import detect

def checkEngAndTranslate(project_text):
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(60)
    global translationTimeout
    language = 'en'
    if project_text == "":
        language = 'en'
    else:
        try:
            language = detect(project_text)
        except:
            print("Error translating")
    print("Language:" + str(language))
    if language == "en":
        return project_text
    if language != "en":
        return ""
        print("Start translating")
        tokens = nltk.word_tokenize(project_text)
        i = 0
        text_to_translate = ""
        translated = ""
        while i < len(tokens):
            for j in range(0, 200):
                if i >= len(tokens):
                    continue
                text_to_translate = text_to_translate + " " + tokens[i]
                i = i + 1
            try:
                en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
            except:
                print("Timeout translation")
                translationTimeout = translationTimeout + 1
                en_text  = ""
            translated = translated + " " + en_text
            text_to_translate = ""
        print(translated)
        project_text = translated
        print("End translating")
        return project_text
    return project_text

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
    si_cls = UniversalClassifier()
    si_cls.load_RF_words_only("SI_RF")
    for res in results:
        print res[0]
        message = ""
        option = "v27 classifier new dataset (naturally balanced) random forests, with 1-4 grams, 08/05/2019"
        objective = 0
        actors = 0
        outputs = 0
        innovativeness = 0
        document_text = ""
        si = 0
        project_id = res[0]
        sql_desc = "Select * from AdditionalProjectData where FieldName like '%Desc%' and (SourceURL not like '%v1%' or SourceURL not like '%v2%')"
        mysql_cursor.execute(sql_desc)
        results_desc = mysql_cursor.fetchall()
        for desc in results_desc:
            document_text = document_text + " "+desc[2]
        documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                no_cursor_timeout=True).batch_size(100)

        for doc in documents:
            txt = doc['translation']
            document_text = document_text+" "+ txt
        if len(document_text)<350 or "domain sale" in document_text:
            documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)},
                                                    no_cursor_timeout=True).batch_size(100)
            document_text = ""
            for doc in documents2:
                document_text = document_text + " "+doc['text']
        if "page not found" in document_text.lower():
            message = "Page not found"
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                        project_id, option, message, si)
            mysql_cursor.execute(sql)
            db_mysql.commit()
        # elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower()\
        #         or "abbiamo appena registrato" in document_text.lower() or "neither the service provider nor the domain owner maintain any relationship with the advertisers." in document_text.lower()\
        #         or "to purchase, call buydomains" in document_text.lower() or "hundreds of thousands of premium domains" in document_text.lower() or "search for a premium domain" in document_text.lower()\
        #         or "This domain is registered for one" in document_text.lower() or "for your website name!" in document_text.lower():
        #     message = "Domain for sale"
        #     sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
        #           "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
        #                                                                 project_id, option, message, si)
        #     mysql_cursor.execute(sql)
        #     db_mysql.commit()
        elif len(document_text)<350:
            message = "Text smaller than 350 characters"
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message,si)
            mysql_cursor.execute(sql)
            db_mysql.commit()
        else:
            objective = objective_cls.predict_words_only([document_text])[0]
            actors = actors_cls.predict_words_only([document_text])[0]
            outputs = outputs_cls.predict_words_only([document_text])[0]
            innovativeness = innovativeness_cls.predict_words_only([document_text])[0]
            si = si_cls.predict_words_only([document_text])[0]
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                        project_id, option, message, si)
            mysql_cursor.execute(sql)
            db_mysql.commit()
    print("Done!")