from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import resample, shuffle
from sklearn.model_selection import cross_val_score
from pymongo import MongoClient
import pickle
import csv
from nltk.stem.snowball import EnglishStemmer

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

sql = '(SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%Kick%") limit 620)union (SELECT * FROM EDSI.TypeOfSocialInnotation where  (SourceModel like "%ManualAnnotation%"))'
cursor.execute(sql)
results = cursor.fetchall()
csv_file = open('for_stat_analysis2_diff_bin_1.csv','w')
csv_writer = csv.writer(csv_file, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
projectList = []
text_array = []
classa = []
objectives = []
actors = []
outputs = []
pro_id = []
innovativeness = []
soci_inno = []
for res in results:
    Outputs = res[1]
    if Outputs>=1:
        bin_Outputs = 1
    else:
        bin_Outputs = 0
    Objectives = res[2]
    if Objectives>=1:
        binObjectives = 1
    else:
        binObjectives = 0
    Actors = res[3]
    if Actors>=1:
        binActors = 1
    else:
        binActors = 0
    Innovativeness = res[4]
    if Innovativeness>=1:
        binInnovativeness =1
    else:
        binInnovativeness = 0
    projectId = res[5]
    SocialInnovation = res[6]
    if SocialInnovation>=1:
        bin_SocialInnovation = 1
    else:
        bin_SocialInnovation = 0
    des_sql = 'SELECT * FROM EDSI.AdditionalProjectData where FieldName like "%Desc%" and Projects_idProjects='+str(projectId)
    cursor.execute(des_sql)
    results2 = cursor.fetchall()
    text = ""
    documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(projectId)},
                                            no_cursor_timeout=True).batch_size(100)
    for res2 in results2:
        text = text + " "+res2[2].encode('utf-8')
    for doc in documents:
        text = text + " "+ doc['translation'].encode('utf-8')
    pro_sql = 'SELECT * FROM EDSI.Projects where idProjects=' + str(projectId)
    cursor.execute(pro_sql)
    pro_res = cursor.fetchall()
    for p in pro_res:
        Pro_name = p[2]
        Pro_Web = p[11]
    topicsEx = []
    q5 = "Select * from Project_Topics where Projects_idProject={0} and (Version like '%v4%' or Version like '%Manual%')".format(
        projectId)
    cursor.execute(q5)
    topics = cursor.fetchall()
    r_topics = []
    pro_id.append(projectId)
    topicsa = ""
    for topic in topics:
        lenght = topic[9]
        score = topic[2]
        topic_name = topic[1]
        if score > 0.7:
            topicsEx.append(
               topic[1])
            topicsa = topicsa + ";"+topic[1]
    text_array.append(text)
    objectives.append(binObjectives)
    actors.append(binActors)
    outputs.append(bin_Outputs)
    innovativeness.append(binInnovativeness)
    soci_inno.append(bin_SocialInnovation)
    classa.append(binActors)
    projectList.append((projectId,Pro_name,Pro_Web,text,topicsa,Outputs,Objectives,Actors,Innovativeness,SocialInnovation,bin_Outputs,binObjectives,binActors,binInnovativeness,bin_SocialInnovation))


df = pd.DataFrame({'project_id':pro_id,'text':text_array,'actors':actors,'objectives':objectives,'outputs':outputs,
                   'innovativeness':innovativeness,'social_innovation':soci_inno})

# df_majority = df[df.classa==1]
# df_minority = df[df.classa==0]
# df_minority_upsampled = resample(df_minority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=300,    # to match majority class
#                                  random_state=83293) # reproducible results
df_upsampled = df
# print df_upsampled
# exit()
print "New dataset"
# Display new class counts
print df_upsampled.actors.value_counts()

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()

stopWords = set(stopwords.words('english'))
text_clf_actor = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_objectives = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_outputs = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_innovativeness = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_social_inno = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_actor.fit(df_upsampled.text, df_upsampled.actors)
text_clf_objectives.fit(df_upsampled.text,df_upsampled.objectives)
text_clf_outputs.fit(df_upsampled.text,df_upsampled.outputs)
text_clf_innovativeness.fit(df_upsampled.text,df_upsampled.innovativeness)
text_clf_social_inno.fit(df_upsampled.text,df_upsampled.social_innovation)
pickle.dump(text_clf_actor, open("model_actors.pkl", 'wb'))
pickle.dump(text_clf_objectives, open("model_objectives.pkl", 'wb'))
pickle.dump(text_clf_outputs, open("model_outputs.pkl", 'wb'))
pickle.dump(text_clf_innovativeness, open("model_innovativeness.pkl", 'wb'))
pickle.dump(text_clf_social_inno, open("model_social_inno.pkl", 'wb'))
#exit(2)


text_clf_actor.fit(df_upsampled.text[0:1200], df_upsampled.actors[0:1200])
text_clf_objectives.fit(df_upsampled.text[0:1200],df_upsampled.objectives[0:1200])
text_clf_outputs.fit(df_upsampled.text[0:1200],df_upsampled.outputs[0:1200])
text_clf_innovativeness.fit(df_upsampled.text[0:1200],df_upsampled.innovativeness[0:1200])
text_clf_social_inno.fit(df_upsampled.text[0:1200],df_upsampled.social_innovation[0:1200])



predictions_actor = text_clf_actor.predict(df_upsampled.text[1200:])
print(classification_report(df_upsampled.actors[1200:],predictions_actor))

predictions_objectives = text_clf_objectives.predict(df_upsampled.text[1200:])
print(classification_report(df_upsampled.objectives[1200:],predictions_objectives))

predictions_outputs = text_clf_outputs.predict(df_upsampled.text[1200:])
print(classification_report(df_upsampled.outputs[1200:],predictions_outputs))

predictions_innovativeness = text_clf_innovativeness.predict(df_upsampled.text[1200:])
print(classification_report(df_upsampled.innovativeness[1200:],predictions_innovativeness))

predictions_social_inno = text_clf_social_inno.predict(df_upsampled.text[1200:])
print(classification_report(df_upsampled.social_innovation[1200:],predictions_social_inno))
csv_writer.writerow(["ProjectID","ProjectName","URL","OrigText","ClassText","Topics","Outputs","Objectives","Actors","Innovativeness","SocialInnovation","bin_Outputs","binObjectives","binActors","binInnovativeness","bin_SocialInnovation","predictions_objectives","predictions_actor","predictions_outputs","predictions_innovativeness","predictions_social_inno"])

i = 0
for index, row in df_upsampled[1200:].iterrows():
    pred = predictions_actor[i]
    pro_id = row['project_id']
    text = row['text']
    for pro in projectList:
        if pro[0]==pro_id:
            if pro[1]!= None:
                name = pro[1].encode('utf-8')
            else:
                name = ""
            if pro[2]!=None:
                url = pro[2].encode('utf-8')
            else:
                url = ""
            if pro[3]!=None:
                OrigTxt = pro[3]
            else:
                OrigTxt = ""
            if text != None:
                text = text
            else:
                text = ""
            csv_writer.writerow([pro_id,name,url,"","",pro[4],pro[5],pro[6],pro[7],pro[8],pro[9],pro[10],pro[11],pro[12],pro[13],pro[14],predictions_objectives[i],predictions_actor[i],predictions_outputs[i],predictions_innovativeness[i],predictions_social_inno[i]])
    i = i + 1


# 2nd part
text_clf_actor = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_objectives = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_outputs = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_innovativeness = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_social_inno = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])
text_clf_actor.fit(df_upsampled.text[400:], df_upsampled.actors[400:])
text_clf_objectives.fit(df_upsampled.text[400:],df_upsampled.objectives[400:])
text_clf_outputs.fit(df_upsampled.text[400:],df_upsampled.outputs[400:])
text_clf_innovativeness.fit(df_upsampled.text[400:],df_upsampled.innovativeness[400:])
text_clf_social_inno.fit(df_upsampled.text[400:],df_upsampled.social_innovation[400:])



predictions_actor = text_clf_actor.predict(df_upsampled.text[0:400])
print(classification_report(df_upsampled.actors[0:400],predictions_actor))

predictions_objectives = text_clf_objectives.predict(df_upsampled.text[0:400])
print(classification_report(df_upsampled.objectives[0:400],predictions_objectives))

predictions_outputs = text_clf_outputs.predict(df_upsampled.text[0:400])
print(classification_report(df_upsampled.outputs[0:400],predictions_outputs))

predictions_innovativeness = text_clf_innovativeness.predict(df_upsampled.text[0:400])
print(classification_report(df_upsampled.innovativeness[0:400],predictions_innovativeness))

predictions_social_inno = text_clf_social_inno.predict(df_upsampled.text[0:400])
print(classification_report(df_upsampled.social_innovation[0:400],predictions_social_inno))
#csv_writer.writerow(["ProjectID","ProjectName","URL","OrigText","ClassText","Topics","Outputs","Objectives","Actors","Innovativeness","SocialInnovation","bin_Outputs","binObjectives","binActors","binInnovativeness","bin_SocialInnovation","predictions_objectives","predictions_actor","predictions_outputs","predictions_innovativeness","predictions_social_inno"])

i = 0
for index, row in df_upsampled[0:400].iterrows():
    pred = predictions_actor[i]
    pro_id = row['project_id']
    text = row['text']
    for pro in projectList:
        if pro[0]==pro_id:
            if pro[1]!= None:
                name = pro[1].encode('utf-8')
            else:
                name = ""
            if pro[2]!=None:
                url = pro[2].encode('utf-8')
            else:
                url = ""
            if pro[3]!=None:
                OrigTxt = pro[3]
            else:
                OrigTxt = ""
            if text != None:
                text = text
            else:
                text = ""
            csv_writer.writerow([pro_id,name,url,"","",pro[4],pro[5],pro[6],pro[7],pro[8],pro[9],pro[10],pro[11],pro[12],pro[13],pro[14],predictions_objectives[i],predictions_actor[i],predictions_outputs[i],predictions_innovativeness[i],predictions_social_inno[i]])
    i = i + 1


# 3nd part
text_clf_actor = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_objectives = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_outputs = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_innovativeness = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_social_inno = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])
text_clf_actor.fit(pd.concat([df_upsampled.text[0:400],df_upsampled.text[800:]]), pd.concat([df_upsampled.actors[0:400],df_upsampled.actors[800:]]))
text_clf_objectives.fit(pd.concat([df_upsampled.text[0:400],df_upsampled.text[800:]]),pd.concat([df_upsampled.objectives[0:400],df_upsampled.objectives[800:]]))
text_clf_outputs.fit(pd.concat([df_upsampled.text[0:400],df_upsampled.text[800:]]),pd.concat([df_upsampled.outputs[0:400],df_upsampled.outputs[800:]]))
text_clf_innovativeness.fit(pd.concat([df_upsampled.text[0:400],df_upsampled.text[800:]]),pd.concat([df_upsampled.innovativeness[0:400],df_upsampled.innovativeness[800:]]))
text_clf_social_inno.fit(pd.concat([df_upsampled.text[0:400],df_upsampled.text[800:]]),pd.concat([df_upsampled.social_innovation[0:400],df_upsampled.social_innovation[800:]]))



predictions_actor = text_clf_actor.predict(df_upsampled.text[400:800])
print(classification_report(df_upsampled.actors[400:800],predictions_actor))

predictions_objectives = text_clf_objectives.predict(df_upsampled.text[400:800])
print(classification_report(df_upsampled.objectives[400:800],predictions_objectives))

predictions_outputs = text_clf_outputs.predict(df_upsampled.text[400:800])
print(classification_report(df_upsampled.outputs[400:800],predictions_outputs))

predictions_innovativeness = text_clf_innovativeness.predict(df_upsampled.text[400:800])
print(classification_report(df_upsampled.innovativeness[400:800],predictions_innovativeness))

predictions_social_inno = text_clf_social_inno.predict(df_upsampled.text[400:800])
print(classification_report(df_upsampled.social_innovation[400:800],predictions_social_inno))
#csv_writer.writerow(["ProjectID","ProjectName","URL","OrigText","ClassText","Topics","Outputs","Objectives","Actors","Innovativeness","SocialInnovation","bin_Outputs","binObjectives","binActors","binInnovativeness","bin_SocialInnovation","predictions_objectives","predictions_actor","predictions_outputs","predictions_innovativeness","predictions_social_inno"])

i = 0
for index, row in df_upsampled[400:800].iterrows():
    pred = predictions_actor[i]
    pro_id = row['project_id']
    text = row['text']
    for pro in projectList:
        if pro[0]==pro_id:
            if pro[1]!= None:
                name = pro[1].encode('utf-8')
            else:
                name = ""
            if pro[2]!=None:
                url = pro[2].encode('utf-8')
            else:
                url = ""
            if pro[3]!=None:
                OrigTxt = pro[3]
            else:
                OrigTxt = ""
            if text != None:
                text = text
            else:
                text = ""
            csv_writer.writerow([pro_id,name,url,"","",pro[4],pro[5],pro[6],pro[7],pro[8],pro[9],pro[10],pro[11],pro[12],pro[13],pro[14],predictions_objectives[i],predictions_actor[i],predictions_outputs[i],predictions_innovativeness[i],predictions_social_inno[i]])
    i = i + 1

# 4nd part
text_clf_actor = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_objectives = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_outputs = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_innovativeness = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

text_clf_social_inno = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])
text_clf_actor.fit(pd.concat([df_upsampled.text[0:800],df_upsampled.text[1200:]]), pd.concat([df_upsampled.actors[0:800],df_upsampled.actors[1200:]]))
text_clf_objectives.fit(pd.concat([df_upsampled.text[0:800],df_upsampled.text[1200:]]),pd.concat([df_upsampled.objectives[0:800],df_upsampled.objectives[1200:]]))
text_clf_outputs.fit(pd.concat([df_upsampled.text[0:800],df_upsampled.text[1200:]]),pd.concat([df_upsampled.outputs[0:800],df_upsampled.outputs[1200:]]))
text_clf_innovativeness.fit(pd.concat([df_upsampled.text[0:800],df_upsampled.text[1200:]]),pd.concat([df_upsampled.innovativeness[0:800],df_upsampled.innovativeness[1200:]]))
text_clf_social_inno.fit(pd.concat([df_upsampled.text[0:800],df_upsampled.text[1200:]]),pd.concat([df_upsampled.social_innovation[0:800],df_upsampled.social_innovation[1200:]]))



predictions_actor = text_clf_actor.predict(df_upsampled.text[800:1200])
print(classification_report(df_upsampled.actors[800:1200],predictions_actor))

predictions_objectives = text_clf_objectives.predict(df_upsampled.text[800:1200])
print(classification_report(df_upsampled.objectives[800:1200],predictions_objectives))

predictions_outputs = text_clf_outputs.predict(df_upsampled.text[800:1200])
print(classification_report(df_upsampled.outputs[800:1200],predictions_outputs))

predictions_innovativeness = text_clf_innovativeness.predict(df_upsampled.text[800:1200])
print(classification_report(df_upsampled.innovativeness[800:1200],predictions_innovativeness))

predictions_social_inno = text_clf_social_inno.predict(df_upsampled.text[800:1200])
print(classification_report(df_upsampled.social_innovation[800:1200],predictions_social_inno))
#csv_writer.writerow(["ProjectID","ProjectName","URL","OrigText","ClassText","Topics","Outputs","Objectives","Actors","Innovativeness","SocialInnovation","bin_Outputs","binObjectives","binActors","binInnovativeness","bin_SocialInnovation","predictions_objectives","predictions_actor","predictions_outputs","predictions_innovativeness","predictions_social_inno"])

i = 0
for index, row in df_upsampled[800:1200].iterrows():
    pred = predictions_actor[i]
    pro_id = row['project_id']
    text = row['text']
    for pro in projectList:
        if pro[0]==pro_id:
            if pro[1]!= None:
                name = pro[1].encode('utf-8')
            else:
                name = ""
            if pro[2]!=None:
                url = pro[2].encode('utf-8')
            else:
                url = ""
            if pro[3]!=None:
                OrigTxt = pro[3]
            else:
                OrigTxt = ""
            if text != None:
                text = text
            else:
                text = ""
            csv_writer.writerow([pro_id,name,url,"","",pro[4],pro[5],pro[6],pro[7],pro[8],pro[9],pro[10],pro[11],pro[12],pro[13],pro[14],predictions_objectives[i],predictions_actor[i],predictions_outputs[i],predictions_innovativeness[i],predictions_social_inno[i]])
    i = i + 1