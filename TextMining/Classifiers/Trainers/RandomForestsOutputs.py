from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.utils import shuffle
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


data_folder = "../../../Helpers/Dataset_afterMay_single/"
ds = DataSet()
total_num_spam = 0
sentences = []
total_num_files = 0
# job = aetros.backend.start_job('nikolamilosevic86/GloveModel')
annotators = [f for f in listdir(data_folder) if isdir(join(data_folder, f))]
for ann in annotators:
    folder = data_folder + "/" + ann
    Annot = Annotator()
    Annot.Name = ann
    ds.Annotators.append(Annot)
    onlyfiles = [f for f in listdir(folder) if (f.endswith(".txt"))]
    for file in onlyfiles:
        Annot.files.append(data_folder + "/" + ann + '/' + file)
        doc = Document()
        total_num_files = total_num_files + 1
        doc.Lines = []
        # doc.Annotations = []
        doc.DocumentName = file
        Annot.documents.append(doc)
        if (file.startswith('a') or file.startswith('t')):
            continue
        print file
        doc.DatabaseID = file.split("_")[1].split(".")[0]
        fl = open(data_folder + "/" + ann + '/' + file, 'r')
        content = fl.read()
        doc.Text = content
        lines = content.split('\n')
        line_index = 0
        for line in lines:
            l = Line()
            l.StartSpan = line_index
            l.EndSpan = line_index + len(line)
            l.Text = line
            line_index = line_index + len(line) + 1
            sentences.append(line)
            doc.Lines.append(l)

        an = open(data_folder + "/" + ann + '/' + file.replace(".txt", ".ann"), 'r')
        annotations = an.readlines()
        for a in annotations:
            a = re.sub(r'\d+;\d+', '', a).replace('  ', ' ')
            split_ann = a.split('\t')
            if (split_ann[0].startswith("T")):
                id = split_ann[0]
                sp_split_ann = split_ann[1].split(' ')
                low_level_ann = sp_split_ann[0]
                if low_level_ann == "ProjectMark":
                    continue
                span_start = sp_split_ann[1]
                span_end = sp_split_ann[2]
                ann_text = split_ann[2]
                Ann = Annotation()
                Ann.AnnotationText = ann_text
                Ann.StartSpan = int(span_start)
                Ann.EndSpan = int(span_end)
                Ann.FromAnnotator = Annot.Name
                Ann.FromFile = file
                Ann.LowLevelClass = low_level_ann
                if (low_level_ann == "SL_Outputs_3"):
                    Ann.HighLevelClass = "Outputs"
                if (
                            low_level_ann == "SL_Objective_1a" or low_level_ann == "SL_Objective_1b" or low_level_ann == "SL_Objective_1c"):
                    Ann.HighLevelClass = "Objectives"
                if (
                            low_level_ann == "SL_Actors_2a" or low_level_ann == "SL_Actors_2b" or low_level_ann == "SL_Actors_2c"):
                    Ann.HighLevelClass = "Actors"
                if (low_level_ann == "SL_Innovativeness_4a"):
                    Ann.HighLevelClass = "Innovativeness"
                doc.Annotations.append(Ann)
                for line in doc.Lines:
                    if line.StartSpan <= Ann.StartSpan and line.EndSpan >= Ann.EndSpan:
                        line.Annotations.append(Ann)

            else:
                id = split_ann[0]
                sp_split_ann = split_ann[1].split(' ')
                mark_name = sp_split_ann[0]
                if (len(sp_split_ann) <= 2):
                    continue
                mark = sp_split_ann[2].replace('\n', '')
                if (mark_name == "DL_Outputs"):
                    doc.Project_Mark_Outputs_3A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectOutputSatisfied = True

                if(mark_name == "DL_Objective"):
                    doc.Project_Mark_Objective_1A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectObjectiveSatisfied = True
                if (mark_name == "DL_Innovativeness" or mark_name == "DL_Innovativeness"):
                    doc.Project_Mark_Innovativeness_3A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectInnovativenessSatisfied = True
                if (mark_name == "DL_Actors_2a" or mark_name == "DL_Actors"):
                    doc.Project_Mark_Actors_2A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectActorSatisfied = True

                if (mark_name == "DL_Outputs_3" or mark_name == "DL_Outputs_3a"):
                    doc.Project_Mark_Outputs_3A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectOutputSatisfied = True
                if (mark_name == "DL_Objective_1a"):
                    doc.Project_Mark_Objective_1A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectObjectiveSatisfied = True
                if (mark_name == "DL_Objective_1b" or mark_name == "DL_Objective"):
                    doc.Project_Mark_Objective_1B = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectObjectiveSatisfied = True
                if (mark_name == "DL_Objective_1c"):
                    doc.Project_Mark_Objective_1C = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectObjectiveSatisfied = True
                if (mark_name == "DL_Innovativeness_4a" or mark_name == "DL_Innovativeness"):
                    doc.Project_Mark_Innovativeness_3A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectInnovativenessSatisfied = True
                if (mark_name == "DL_Actors_2a" or mark_name == "DL_Actors"):
                    doc.Project_Mark_Actors_2A = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectActorSatisfied = True
                if (mark_name == "DL_Actors_2b"):
                    doc.Project_Mark_Actors_2B = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectActorSatisfied = True
                if (mark_name == "DL_Actors_2c"):
                    doc.Project_Mark_Actors_2C = int(mark)
                    if int(mark) >= 1:
                        doc.isProjectActorSatisfied = True
        if (
                                            doc.Project_Mark_Objective_1A == 0 and doc.Project_Mark_Objective_1B == 0 and doc.Project_Mark_Objective_1C == 0 and doc.Project_Mark_Actors_2A == 0
                        and doc.Project_Mark_Actors_2B == 0 and doc.Project_Mark_Actors_2B == 0 and doc.Project_Mark_Actors_2C == 0 and doc.Project_Mark_Outputs_3A == 0
        and doc.Project_Mark_Innovativeness_3A == 0):
            doc.isSpam = True
            total_num_spam = total_num_spam + 1

i = 0
j = i + 1
kappa_files = 0

done_documents = []
num_overlap_spam = 0
num_spam = 0

total_objectives = 0
total_outputs = 0
total_actors = 0
total_innovativeness = 0
ann1_annotations_objectives = []
ann2_annotations_objectives = []
ann1_annotations_actors = []
ann2_annotations_actors = []
ann1_annotations_outputs = []
ann2_annotations_outputs = []
ann1_annotations_innovativeness = []
ann2_annotations_innovativeness = []
match_objectives = 0
match_outputs = 0
match_actors = 0
match_innovativeness = 0

while i < len(ds.Annotators) - 1:
    while j < len(ds.Annotators):
        annotator1 = ds.Annotators[i]
        annotator2 = ds.Annotators[j]
        for doc1 in annotator1.documents:
            for doc2 in annotator2.documents:
                if doc1.DocumentName == doc2.DocumentName and doc1.DocumentName not in done_documents:
                    done_documents.append(doc1.DocumentName)
                    line_num = 0

                    ann1_objective = [0] * len(doc1.Lines)
                    ann2_objective = [0] * len(doc2.Lines)
                    ann1_output = [0] * len(doc1.Lines)
                    ann2_output = [0] * len(doc2.Lines)
                    ann1_actor = [0] * len(doc1.Lines)
                    ann2_actor = [0] * len(doc2.Lines)
                    ann1_innovativeness = [0] * len(doc1.Lines)
                    ann2_innovativeness = [0] * len(doc2.Lines)
                    while line_num < len(doc1.Lines):
                        if len(doc1.Lines[line_num].Annotations) > 0:
                            for a in doc1.Lines[line_num].Annotations:
                                if a.HighLevelClass == "Objectives":
                                    ann1_objective[line_num] = 1
                                    total_objectives = total_objectives + 1
                                if a.HighLevelClass == "Outputs":
                                    ann1_output[line_num] = 1
                                    total_outputs = total_outputs + 1
                                if a.HighLevelClass == "Actors":
                                    ann1_actor[line_num] = 1
                                    total_actors = total_actors + 1
                                if a.HighLevelClass == "Innovativeness":
                                    ann1_innovativeness[line_num] = 1
                                    total_innovativeness = total_innovativeness + 1
                                for a1 in doc2.Lines[line_num].Annotations:
                                    if a1.HighLevelClass == a.HighLevelClass:
                                        if a1.HighLevelClass == "Objectives":
                                            match_objectives = match_objectives + 1
                                        if a1.HighLevelClass == "Outputs":
                                            match_outputs = match_outputs + 1
                                        if a1.HighLevelClass == "Actors":
                                            match_actors = match_actors + 1
                                        if a1.HighLevelClass == "Innovativeness":
                                            match_innovativeness = match_innovativeness + 1
                        if len(doc2.Lines[line_num].Annotations) > 0:
                            for a in doc2.Lines[line_num].Annotations:
                                if a.HighLevelClass == "Objectives":
                                    ann2_objective[line_num] = 1
                                    total_objectives = total_objectives + 1
                                if a.HighLevelClass == "Outputs":
                                    ann2_output[line_num] = 1
                                    total_outputs = total_outputs + 1
                                if a.HighLevelClass == "Actors":
                                    ann2_actor[line_num] = 1
                                    total_actors = total_actors + 1
                                if a.HighLevelClass == "Innovativeness":
                                    ann2_innovativeness[line_num] = 1
                                    total_innovativeness = total_innovativeness + 1
                        line_num = line_num + 1
                    ann1_annotations_outputs.extend(ann1_output)
                    ann2_annotations_outputs.extend(ann2_output)
                    ann1_annotations_objectives.extend(ann1_objective)
                    ann2_annotations_objectives.extend(ann2_objective)
                    ann1_annotations_actors.extend(ann1_actor)
                    ann2_annotations_actors.extend(ann2_actor)
                    ann1_annotations_innovativeness.extend(ann1_innovativeness)
                    ann2_annotations_innovativeness.extend(ann2_innovativeness)
                    print "Statistics for document:" + doc1.DocumentName
                    print "Annotators " + annotator1.Name + " and " + annotator2.Name
                    print "Spam by " + annotator1.Name + ":" + str(doc1.isSpam)
                    print "Spam by " + annotator2.Name + ":" + str(doc2.isSpam)
                    if (doc1.isSpam == doc2.isSpam):
                        num_overlap_spam = num_overlap_spam + 1
                    if doc1.isSpam:
                        num_spam = num_spam + 1
                    if doc2.isSpam:
                        num_spam = num_spam + 1
                    kappa_files = kappa_files + 1
        j = j + 1
    i = i + 1
    j = i + 1

print annotators
doc_array = []
text_array = []
objectives = []
actors = []
outputs = []
innovativeness = []
for ann in ds.Annotators:
    for doc in ann.documents:
        doc_array.append(
            [doc.Text, doc.isProjectObjectiveSatisfied, doc.isProjectActorSatisfied, doc.isProjectOutputSatisfied,
             doc.isProjectInnovativenessSatisfied])
        objectives.append(doc.isProjectObjectiveSatisfied)
        actors.append(doc.isProjectActorSatisfied)
        outputs.append(doc.isProjectOutputSatisfied)
        innovativeness.append(doc.isProjectInnovativenessSatisfied)
        text_array.append(doc.Text)
df = pd.DataFrame({'text':text_array,'classa':outputs})

df_majority = df[df.classa==1]
df_minority = df[df.classa==0]
# df_minority_upsampled = resample(df_minority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=300,    # to match majority class
#                                  random_state=83293) # reproducible results
df_upsampled = pd.concat([df_majority, df_minority])
# print df_upsampled
# exit()
print "New dataset"
# Display new class counts
print df_upsampled.classa.value_counts()

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()
#print df_upsampled

# train = text_array[0:int(0.8*len(text_array))]
# train_Y = innovativeness[0:int(0.8*len(actors))]
#
# test = text_array[int(0.8*len(text_array)):]
# test_Y = innovativeness[int(0.8*len(actors)):]

#categories = ['non actor', 'actor']

text_clf = Pipeline([('vect', CountVectorizer()),
                      ('tfidf', TfidfTransformer()),
                      ('clf', RandomForestClassifier(n_estimators=300, max_depth=None, random_state=0)),
 ])

scores = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='f1')
final = 0
for score in scores:
    final = final + score
print scores
print "Final:" + str(final/10)


scores1 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='precision')
final = 0
print "Precision"
for score in scores1:
    final = final + score
print scores1
print "Final:" + str(final/10)

scores2 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='recall')
final = 0
print "Recall"
for score in scores2:
    final = final + score
print scores2
print "Final:" + str(final/10)

text_clf.fit( df_upsampled.text, df_upsampled.classa)
filename = '../Models/random_forests_outputs.sav'
pickle.dump(text_clf, open(filename, 'wb'))
