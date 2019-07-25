import os
from sklearn.feature_extraction.text import CountVectorizer
from pymongo import MongoClient
from bert_text import run_on_dfs
from nltk.stem.snowball import EnglishStemmer
import text_cleaner

import MySQLdb
from database_access import *

stemmer = EnglishStemmer()
mongo_client = MongoClient()
mongo_db = mongo_client.ESID
analyzer = CountVectorizer().build_analyzer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))

db = MySQLdb.connect(host, username, password, database, charset='utf8')
cursor = db.cursor()

sql = '(SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%Kick%") limit 800)union (SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%ManualAnnotation%"))'
#sql = 'SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%ManualAnnotation%")'

cursor.execute(sql)
results = cursor.fetchall()
projectList = []
text_array = []
classa = []
for res in results:
    Outputs = res[1]
    id = res[5]
    if Outputs>1:
        bin_Outputs = "Pos"
    else:
        bin_Outputs = "Neg"
    Objectives = res[2]
    if Objectives>1:
        binObjectives = "Pos"
    else:
        binObjectives = "Neg"
    Actors = res[3]
    if Actors>1:
        binActors =  "Pos"
    else:
        binActors = "Neg"
    Innovativeness = res[4]
    if Innovativeness>1:
        binInnovativeness ="Pos"
    else:
        binInnovativeness = "Neg"
    projectId = res[5]
    SocialInnovation = res[6]
    if SocialInnovation == None:
        continue
    if SocialInnovation>1:
        bin_SocialInnovation = "Pos"
    else:
        bin_SocialInnovation = "Neg"
    des_sql = 'SELECT * FROM EDSI.AdditionalProjectData where FieldName like "%Desc%" and Projects_idProjects='+str(projectId)
    cursor.execute(des_sql)
    results2 = cursor.fetchall()
    text = ""
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(projectId)},
                                            no_cursor_timeout=True).batch_size(100)
    for res2 in results2:
        text = text + " "+res2[2]
    for doc in documents:
        text = text + " "+ doc['translation']
    new_text = text_cleaner.clean_text(text)
    if len(new_text)<200:
        continue
    text_array.append(new_text)
    classa.append(binObjectives)
    projectList.append((new_text,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))
    if binInnovativeness=="Pos":
        if not os.path.exists("PosIno"):
            os.mkdir("PosIno")
        fl = open("PosIno/"+str(id)+".txt",'w')
        fl.write(new_text)
        fl.close()
    else:
        if not os.path.exists("NegIno"):
            os.mkdir("NegIno")
        fl = open("NegIno/" + str(id) + ".txt", 'w')
        fl.write(new_text)
        fl.close()