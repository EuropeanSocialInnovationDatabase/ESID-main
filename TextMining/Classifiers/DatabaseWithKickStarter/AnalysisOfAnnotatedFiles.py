
from os import listdir
from os.path import isfile, join
import csv

import pickle

from nltk.stem.snowball import EnglishStemmer
from sklearn.feature_extraction.text import CountVectorizer

csv_file = open('StevenKickStarter.csv','w')
csv_writer = csv.writer(csv_file, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)

folder_path = "../../../../Software/brat-v1.3_Crunchy_Frog/data/0_Flag_SI_July_Task/KickStarterSteven/"
onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
stemmer = EnglishStemmer()
analyzer = CountVectorizer().build_analyzer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))

model_actors = pickle.load(open("model_actors.pkl", 'rb'))
model_objectives = pickle.load(open("model_objectives.pkl", 'rb'))
model_outputs = pickle.load(open("model_outputs.pkl", 'rb'))
model_innovativeness = pickle.load(open("model_innovativeness.pkl", 'rb'))
model_social_inno = pickle.load(open("model_social_inno.pkl", 'rb'))
csv_writer.writerow(["name","text","marked objective","marked actor","marked output","marked innovativeness","marked si","predicted objective","predicted actor","predicted output","predicted innovativeness","predicted social innovation"])
for f in onlyfiles:
    if f.endswith('.txt'):
        objective = 0
        actor = 0
        output = 0
        innovativeness = 0
        si_mark = 0
        pred_objective = 0
        pred_actor = 0
        pred_output = 0
        pred_innovativeness = 0
        pred_si_mark = 0
        filename = f
        text = open(folder_path+f,"r").read()
        pred_objective = model_objectives.predict([text])[0]
        pred_actor = model_actors.predict([text])[0]
        pred_output = model_outputs.predict([text])[0]
        pred_innovativeness = model_innovativeness.predict([text])[0]
        pred_si_mark = model_social_inno.predict([text])[0]
        ann_file = f.replace('.txt','.ann')
        a_lines = open(folder_path+ann_file,'r').readlines()
        for l in a_lines:
            pts = l.split('\t')
            if len(pts)<2:
                continue
            if 'DL_Actors' in pts[1]:
                actor = int(pts[1].replace('\n','').split(' ')[2])
            if 'DL_SocialInnovation' in pts[1]:
                si_mark = int(pts[1].replace('\n','').split(' ')[2])
            if 'DL_Innovativeness' in pts[1]:
                innovativeness = int(pts[1].replace('\n','').split(' ')[2])
            if 'DL_Objective' in pts[1]:
                objective = int(pts[1].replace('\n','').split(' ')[2])
            if 'DL_Outputs' in pts[1]:
                output = int(pts[1].replace('\n','').split(' ')[2])

        csv_writer.writerow([filename,text,objective,actor,output,innovativeness,si_mark,pred_objective,pred_actor,pred_output,pred_innovativeness,pred_si_mark])
