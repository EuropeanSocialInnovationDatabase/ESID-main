from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd
import re
from os import listdir
from os.path import  join,isdir
from sklearn.utils import resample
from sklearn.model_selection import cross_val_score
import pickle

from sklearn.utils import resample

class DataSet:
    Annotators = []
    def __init__(self):
        self.Annotators = []

class Annotator:
    files = []
    documents = []
    Name = ""
    def __init__(self):
        self.files = []
        self.documents = []
        self.Name = ""

class Document:
    Lines = []
    DocumentName = ""
    DatabaseID = ""
    Annotations = []
    Text = ""
    isSpam = False
    Project_Mark_Objective_1A = 0
    Project_Mark_Objective_1B = 0
    Project_Mark_Objective_1C = 0
    Project_Mark_Actors_2A = 0
    Project_Mark_Actors_2B = 0
    Project_Mark_Actors_2C = 0
    Project_Mark_Outputs_3A = 0
    Project_Mark_Innovativeness_3A = 0

    isProjectObjectiveSatisfied = False
    isProjectActorSatisfied = False
    isProjectOutputSatisfied = False
    isProjectInnovativenessSatisfied = False

    isProjectObjectiveSatisfied_predicted = False
    isProjectActorSatisfied_predicted = False
    isProjectOutputSatisfied_predicted = False
    isProjectInnovativenessSatisfied_predicted = False

    def __init__(self):
        self.Text = ""
        self.Lines = []
        self.DocumentName = ""
        self.DatabaseID = ""
        self.Annotations = []
        self.isSpam = False
        self.Project_Mark_Objective_1A = 0
        self.Project_Mark_Objective_1B = 0
        self.Project_Mark_Objective_1C = 0
        self.Project_Mark_Actors_2A = 0
        self.Project_Mark_Actors_2B = 0
        self.Project_Mark_Actors_2C = 0
        self.Project_Mark_Outputs_3A = 0
        self.Project_Mark_Innovativeness_3A = 0
        self.Project_Mark_Innovativeness_3A = 0
        self.isProjectObjectiveSatisfied = False
        self.isProjectActorSatisfied = False
        self.isProjectOutputSatisfied = False
        self.isProjectInnovativenessSatisfied = False

        self.isProjectObjectiveSatisfied_predicted = False
        self.isProjectActorSatisfied_predicted = False
        self.isProjectOutputSatisfied_predicted = False
        self.isProjectInnovativenessSatisfied_predicted = False


class Line:
    StartSpan = 0
    EndSpan = 0
    Text = ""
    Sentences = []
    Tokens = []
    Annotations = []
    def __init__(self):
        self.StartSpan = 0
        self.EndSpan = 0
        self.Text = ""
        self.Sentences = []
        self.Tokens = []
        self.Annotations = []


class Sentence:
    SentenceText = ""
    StartSpan = -1
    EndSpan = -1
    Annotations = []
    def __init__(self):
        self.SentenceText = ""
        self.StartSpan = -1
        self.EndSpan = -1
        self.Annotations = []

class Annotation:
    FromFile = ""
    FromAnnotator = ""
    AnnotationText = ""
    StartSpan = -1
    EndSpan = -1
    HighLevelClass = ""
    LowLevelClass = ""


data_folder = "../../Sample"
onlyfiles = [f for f in listdir(data_folder) if (f.endswith(".txt"))]
texts = []
for f in onlyfiles:
    fa = open(data_folder+"/"+f,"r")
    txt = fa.read()
    texts.append(txt)

TP = 0
FP = 0
FN = 0

i = 0
innovative_1 = 0
innovative_2 = 0
innovative_3 = 0
for sample in texts:
    if "innovation" in sample or "innovative" in sample or "novelty" in sample:
        innovative_1 = innovative_1 + 1
        if sample[4] == True:
            TP = TP+1
        if sample[4] == False:
            FP = FP+1
    else:
        if sample[4]==True:
            FN = FN + 1
    i = i + 1

# precision = float(TP)/float(TP+FP)
# recall = float(TP)/float(TP+FN)
# f_score = 2*precision*recall/(precision+recall)
# print "Innovation rule classifier"
# print "False positives:"+str(FP)
# print "False negatives:"+str(FN)
# print "True positive:"+str(TP)
# print "Precision: "+str(precision)
# print "Recall: "+str(recall)
# print "F1-score: "+str(f_score)

TP = 0
FP = 0
FN = 0
i = 0
for sample in texts:
    if ("new" in sample or "novel" in sample or "alternative" in sample or "improved" in sample or "cutting edge" in sample or "better" in sample)\
            and ("method" in sample or "product" in sample or "service" in sample or "application" in sample or "technology" in sample or "practice" in sample):
        innovative_2 = innovative_2 +1
        if sample[4] == True:
            TP = TP+1
        if sample[4] == False:
            FP = FP+1
    else:
        if sample[4]==True:
            FN = FN + 1
    i = i + 1
# precision = float(TP)/float(TP+FP)
# recall = float(TP)/float(TP+FN)
# f_score = 2*precision*recall/(precision+recall)
# print "Other rule classifier"
# print "False positives:"+str(FP)
# print "False negatives:"+str(FN)
# print "True positive:"+str(TP)
# print "Precision: "+str(precision)
# print "Recall: "+str(recall)
# print "F1-score: "+str(f_score)


TP = 0
FP = 0
FN = 0
i = 0
for sample in texts:
    isInnovative = False
    if ("method" in sample or "product" in sample or "service" in sample or "application" in sample or "technology" in sample or "practice" in sample):

        list_items = ["method","product","service","application","technology","practice"]
        index_list = []
        for item in list_items:
            indexes = [m.start() for m in re.finditer(item, sample)]
            index_list.extend(indexes)

        for index in index_list:
            end = len(sample)
            start = 0
            if index - 500>0:
                start = index - 500
            if index + 500<len(sample):
                end = index + 500
            substr = sample[start:end]
            if ("new" in substr or "novel" in substr or "alternative" in substr or "improved" in substr or "cutting edge" in substr or "better" in substr):
                isInnovative = True


        if isInnovative:
            innovative_3 = innovative_3 + 1
            if sample[4] == True:
                TP = TP+1
            if sample[4] == False:
                FP = FP+1
        else:
            if sample[4]==True:
                FN = FN + 1
# precision = float(TP)/float(TP+FP)
# recall = float(TP)/float(TP+FN)
# f_score = 2*precision*recall/(precision+recall)
# print "Third rule classifier"
# print "False positives:"+str(FP)
# print "False negatives:"+str(FN)
# print "True positive:"+str(TP)
# print "Precision: "+str(precision)
# print "Recall: "+str(recall)
# print "F1-score: "+str(f_score)

TP = 0
FP = 0
FN = 0
i = 0
innovative_4 = 0
for sample in texts:
    isInnovative = False
    if "innovation" in sample or "innovative" in sample or "novelty" in sample:
        isInnovative = True
    if ("method" in sample or "product" in sample or "service" in sample or "application" in sample or "technology" in sample or "practice" in sample):

        list_items = ["method","product","service","application","technology","practice"]
        index_list = []
        for item in list_items:
            indexes = [m.start() for m in re.finditer(item, sample)]
            index_list.extend(indexes)

        for index in index_list:
            end = len(sample)
            start = 0
            if index - 500>0:
                start = index - 500
            if index + 500<len(sample):
                end = index + 500
            substr = sample[start:end]
            if ("new" in substr or "novel" in substr or "alternative" in substr or "improved" in substr or "cutting edge" in substr or "better" in substr):
                isInnovative = True


    if isInnovative:
        innovative_4 = innovative_4 + 1
        if sample[4] == True:
            TP = TP+1
        if sample[4] == False:
            FP = FP+1
    else:
        if sample[4]==True:
            FN = FN + 1

print ""
print "Innovative 1:"+str(innovative_1)
print "Innovative 2:"+str(innovative_2)
print "Innovative 3:"+str(innovative_3)
print "Innovative 4 (1+3):"+str(innovative_4)




