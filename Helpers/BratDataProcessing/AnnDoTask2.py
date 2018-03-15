import nltk
from os import listdir
from os.path import isfile, join,isdir
import csv
import re
import sklearn.metrics
import numpy
from database_access import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold
import numpy as np
import  os
import MySQLdb
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
    FromDataset = ""
    URL = ""
    isSpam = False
    Project_Mark_Objective_1A = 0
    Project_Mark_Objective_1B = 0
    Project_Mark_Objective_1C = 0
    Project_Mark_Actors_2A = 0
    Project_Mark_Actors_2B = 0
    Project_Mark_Actors_2C = 0
    Project_Mark_Outputs_3A = 0
    Project_Mark_Innovativeness_3A = 0
    Mark_Total_Objective = 0
    Mark_Total_Actors = 0
    Mark_Total_Outputs = 0
    Mark_Total_Innovativeness = 0

    isProjectObjectiveSatisfied = False
    isProjectActorSatisfied = False
    isProjectOutputSatisfied = False
    isProjectInnovativenessSatisfied = False

    isProjectObjectiveSatisfied_predicted = False
    isProjectActorSatisfied_predicted = False
    isProjectOutputSatisfied_predicted = False
    isProjectInnovativenessSatisfied_predicted = False

    isSpam_mark_based = False
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
        self.Mark_Total_Objective = 0
        self.Mark_Total_Actors = 0
        self.Mark_Total_Outputs = 0
        self.Mark_Total_Innovativeness = 0
        self.isProjectObjectiveSatisfied = False
        self.isProjectActorSatisfied = False
        self.isProjectOutputSatisfied = False
        self.isProjectInnovativenessSatisfied = False

        self.isProjectObjectiveSatisfied_predicted = False
        self.isProjectActorSatisfied_predicted = False
        self.isProjectOutputSatisfied_predicted = False
        self.isProjectInnovativenessSatisfied_predicted = False
        self.isSpam_mark_based = False
        self.FromDataset = ""
        self.URL = ""


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

class InterAnnotation:
    Annotator1 = ""
    Annotator2 = ""
    AgreementProjects_Objectives = 0
    AgreementProjects_Outputs = 0
    AgreementProjects_Actors = 0
    AgreementProjects_Innovativeness = 0
    TotalOverlappingProjects = 0
    AgreementSpam = 0
    AgreementSpamSI = 0

    def __init__(self):
        self.Annotator1 = ""
        self.Annotator2 = ""
        self.AgreementProjects_Objectives = 0
        self.AgreementProjects_Outputs = 0
        self.AgreementProjects_Actors = 0
        self.AgreementProjects_Innovativeness = 0
        self.AgreementSpam = 0
        self.AgreementSpamSI = 0
        self.TotalOverlappingProjects = 0

class DocumentListItem:
    Name = ""
    objectives = []
    actors = []
    outputs = []
    innovativness = []
    objectives_sd = 0
    actors_sd = 0
    outputs_sd = 0
    innovativness_sd = 0
    def __init__(self):
        self.Name = ""
        self.objectives = []
        self.actors = []
        self.outputs = []
        self.innovativness = []
        self.objectives_sd = 0
        self.actors_sd = 0
        self.outputs_sd = 0
        self.innovativness_sd = 0

if __name__ == '__main__':
    data_folder = "../AnnotationsFinal"
    conflict_folder = "../Conflicts2"
    conflict_folder2 = "../Conflicts21"
    agreeing_docs_objectives = {}
    agreeing_docs_outputs = {}
    agreeing_docs_actors = {}
    agreeing_docs_innovativeness = {}
    if not os.path.exists(conflict_folder):
        os.makedirs(conflict_folder)
    if not os.path.exists(conflict_folder2):
        os.makedirs(conflict_folder2)
    spam_mark = 3
    ds = DataSet()
    total_num_spam = 0
    total_num_spam_mark_based = 0
    total_num_files = 0
    DocumentList = []

    count_objectives_overlap_mark0 = 0
    count_objectives_overlap_mark1 = 0
    count_objectives_overlap_mark2 = 0
    count_objectives_overlap_mark3 = 0
    count_actors_overlap_mark0 = 0
    count_actors_overlap_mark1 = 0
    count_actors_overlap_mark2 = 0
    count_actors_overlap_mark3 = 0
    count_outputs_overlap_mark0 = 0
    count_outputs_overlap_mark1 = 0
    count_outputs_overlap_mark2 = 0
    count_outputs_overlap_mark3 = 0
    count_innovativeness_overlap_mark0 = 0
    count_innovativeness_overlap_mark1 = 0
    count_innovativeness_overlap_mark2 = 0
    count_innovativeness_overlap_mark3 = 0



    count_objectives_mark0 = 0
    count_objectives_mark1 = 0
    count_objectives_mark2 = 0
    count_objectives_mark3 = 0
    count_actors_mark0 = 0
    count_actors_mark1 = 0
    count_actors_mark2 = 0
    count_actors_mark3 = 0
    count_outputs_mark0 = 0
    count_outputs_mark1 = 0
    count_outputs_mark2 = 0
    count_outputs_mark3 = 0
    count_innovativeness_mark0 = 0
    count_innovativeness_mark1 = 0
    count_innovativeness_mark2 = 0
    count_innovativeness_mark3 = 0
    interAnnotatorsData = []
    annotators = [f for f in listdir(data_folder) if isdir(join(data_folder, f))]
    for ann in annotators:
        folder = data_folder+"/"+ann
        Annot = Annotator()
        Annot.Name = ann
        ds.Annotators.append(Annot)
        onlyfiles = [f for f in listdir(folder) if (f.endswith(".txt"))]
        for file in onlyfiles:
            Annot.files.append(data_folder+"/"+ann+'/'+file)
            doc = Document()
            total_num_files = total_num_files + 1
            doc.Lines = []
            #doc.Annotations = []
            isDocumentInList = False
            d = None
            for dd in DocumentList:
                if dd.Name == file:
                    isDocumentInList = True
                    d = dd
            if isDocumentInList == False:
                d = DocumentListItem()
                d.Name = file
                DocumentList.append(d)
            doc.DocumentName= file
            doc.URL = file.replace("p_","").replace(".txt","")

            Annot.documents.append(doc)
            if(file.startswith('a') or file.startswith('t')):
                continue
            print file
            doc.DatabaseID = file.split("_")[1].split(".")[0]
            fl = open(data_folder+"/"+ann+'/'+file,'r')
            content = fl.read()
            doc.Text = content
            lines = content.split('\n')
            line_index = 0
            for line in lines:
                l = Line()
                l.StartSpan = line_index
                l.EndSpan = line_index+len(line)
                l.Text = line
                line_index = line_index+len(line)+1
                doc.Lines.append(l)


            an = open(data_folder+"/"+ann+'/'+file.replace(".txt",".ann"),'r')
            annotations = an.readlines()
            for a in annotations:
                a = re.sub(r'\d+;\d+','',a).replace('  ',' ')
                split_ann = a.split('\t')
                if (split_ann[0].startswith("T")):
                    id = split_ann[0]
                    sp_split_ann = split_ann[1].split(' ')
                    low_level_ann = sp_split_ann[0]
                    if low_level_ann=="ProjectMark":
                        continue
                    if low_level_ann=="SpamProject":
                        doc.isSpam = True
                        doc.isProjectInnovativenessSatisfied = False
                        doc.isProjectOutputSatisfied = False
                        doc.isProjectObjectiveSatisfied = False
                        doc.isProjectActorSatisfied = False
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
                    if(low_level_ann == "SL_Outputs_3a" or low_level_ann == "SL_Outputs_3"):
                        Ann.HighLevelClass = "Outputs"
                    if (low_level_ann == "SL_Objective_1a" or low_level_ann == "SL_Objective_1b" or low_level_ann == "SL_Objective_1c" or low_level_ann == "SL_Objective_1"):
                        Ann.HighLevelClass = "Objectives"
                    if (low_level_ann == "SL_Actors_2a" or low_level_ann == "SL_Actors_2b" or low_level_ann == "SL_Actors_2c" or low_level_ann == "SL_Actors_2"):
                        Ann.HighLevelClass = "Actors"
                    if (low_level_ann == "SL_Innovativeness_4a" or low_level_ann == "SL_Innovativeness_4"):
                        Ann.HighLevelClass = "Innovativeness"
                    doc.Annotations.append(Ann)
                    for line in doc.Lines:
                        if line.StartSpan<=Ann.StartSpan and line.EndSpan>=Ann.EndSpan:
                            line.Annotations.append(Ann)
                else:
                    print split_ann
                    id = split_ann[0]
                    sp_split_ann = split_ann[1].split(' ')
                    mark_name = sp_split_ann[0]
                    if (len(sp_split_ann)<=2):
                        continue
                    mark = sp_split_ann[2].replace('\n','')
                    if(mark_name=="DL_Outputs_3a"):
                        doc.Project_Mark_Outputs_3A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectOutputSatisfied = True
                    if (mark_name == "DL_Objective_1a"):
                        doc.Project_Mark_Objective_1A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Objective_1b"):
                        doc.Project_Mark_Objective_1B = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Objective_1c"):
                        doc.Project_Mark_Objective_1C = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Innovativeness_4a"):
                        doc.Project_Mark_Innovativeness_3A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectInnovativenessSatisfied = True
                    if (mark_name == "DL_Actors_2a"):
                        doc.Project_Mark_Actors_2A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Actors_2b"):
                        doc.Project_Mark_Actors_2B = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Actors_2c"):
                        doc.Project_Mark_Actors_2C = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Objective"):
                        doc.Project_Mark_Objective_1A = int(mark)
                        doc.Project_Mark_Objective_1B = int(mark)
                        doc.Project_Mark_Objective_1C = int(mark)

                        doc.Mark_Total_Objective = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Actors"):
                        doc.Project_Mark_Actors_2A = int(mark)
                        doc.Project_Mark_Actors_2B = int(mark)
                        doc.Project_Mark_Actors_2C = int(mark)
                        doc.Mark_Total_Actors = int(mark)

                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Outputs"):
                        doc.Project_Mark_Outputs_3A = int(mark)
                        doc.Mark_Total_Outputs = int(mark)

                        if int(mark)>=2:
                            doc.isProjectOutputSatisfied = True
                    if (mark_name == "DL_Innovativeness"):
                        doc.Project_Mark_Innovativeness_3A = int(mark)
                        doc.Mark_Total_Innovativeness = int(mark)

                        if int(mark)>=2:
                            doc.isProjectInnovativenessSatisfied = True

            mark = doc.Mark_Total_Objective = max([doc.Project_Mark_Objective_1A,doc.Project_Mark_Objective_1B,doc.Project_Mark_Objective_1C])
            if mark == 0:
                count_objectives_mark0 = count_objectives_mark0 + 1
            if mark == 1:
                count_objectives_mark1 = count_objectives_mark1 + 1
            if mark == 2:
                count_objectives_mark2 = count_objectives_mark2 + 1
            if mark == 3:
                count_objectives_mark3 = count_objectives_mark3 + 1
            mark = doc.Mark_Total_Actors = max([doc.Project_Mark_Actors_2A,doc.Project_Mark_Actors_2B,doc.Project_Mark_Actors_2C])
            if mark == 0:
                count_actors_mark0 = count_actors_mark0 + 1
            if mark == 1:
                count_actors_mark1 = count_actors_mark1 + 1
            if mark == 2:
                count_actors_mark2 = count_actors_mark2 + 1
            if mark == 3:
                count_actors_mark3 = count_actors_mark3 + 1
            mark = doc.Mark_Total_Outputs = max([doc.Project_Mark_Outputs_3A])
            if mark == 0:
                count_outputs_mark0 = count_outputs_mark0 + 1
            if mark == 1:
                count_outputs_mark1 = count_outputs_mark1 + 1
            if mark == 2:
                count_outputs_mark2 = count_outputs_mark2 + 1
            if mark == 3:
                count_outputs_mark3 = count_outputs_mark3 + 1
            mark = doc.Mark_Total_Innovativeness = max([doc.Project_Mark_Innovativeness_3A])
            if mark == 0:
                count_innovativeness_mark0 = count_innovativeness_mark0 + 1
            if mark == 1:
                count_innovativeness_mark1 = count_innovativeness_mark1 + 1
            if mark == 2:
                count_innovativeness_mark2 = count_innovativeness_mark2 + 1
            if mark == 3:
                count_innovativeness_mark3 = count_innovativeness_mark3 + 1

            d.objectives.append(doc.Mark_Total_Objective)
            d.actors.append(doc.Mark_Total_Actors)
            d.outputs.append(doc.Mark_Total_Outputs)
            d.innovativness.append(doc.Mark_Total_Innovativeness)


            if(doc.Mark_Total_Objective+doc.Mark_Total_Actors+doc.Mark_Total_Outputs+doc.Mark_Total_Innovativeness<=spam_mark):
                doc.isSpam_mark_based = True
                total_num_spam_mark_based = total_num_spam_mark_based+1


            if(doc.Project_Mark_Objective_1A==0 and doc.Project_Mark_Objective_1B == 0 and doc.Project_Mark_Objective_1C==0 and doc.Project_Mark_Actors_2A==0
                and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2C==0 and doc.Project_Mark_Outputs_3A == 0
                and doc.Project_Mark_Innovativeness_3A==0):
                doc.isSpam = True
                doc.isSpam_mark_based = True
                total_num_spam = total_num_spam + 1
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    with open('annotations.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        for ann in ds.Annotators:
            for doc in ann.documents:
                sql = "SELECT * from Projects where idProjects='{0}' or ProjectWebpage like '%{1}%'".format(doc.URL,doc.URL)
                cursor.execute(sql)
                results = cursor.fetchall()
                for res in results:
                    doc.FromDataset = res[15]
                for annot in doc.Annotations:
                    spamwriter.writerow([annot.FromFile,annot.FromAnnotator,annot.AnnotationText,annot.LowLevelClass,annot.HighLevelClass,annot.StartSpan,annot.EndSpan])
    i = 0
    j = i+1
    kappa_files = 0

    done_documents = []
    num_overlap_spam = 0
    num_spam = 0
    num_spam_mark_based = 0

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
    dataset = ds
    for doc in ds.Annotators[0].documents:
        agreeing_docs_objectives[doc.DocumentName] = 0
        agreeing_docs_outputs[doc.DocumentName] = 0
        agreeing_docs_actors[doc.DocumentName] = 0
        agreeing_docs_innovativeness[doc.DocumentName] = 0
    while i<len(ds.Annotators)-1:
        while j<len(ds.Annotators):
            interAnn = InterAnnotation()
            interAnn.Annotator1 = ds.Annotators[i].Name
            interAnn.Annotator2 = ds.Annotators[j].Name
            interAnnotatorsData.append(interAnn)
            annotator1 = ds.Annotators[i]
            annotator2 = ds.Annotators[j]
            for doc1 in annotator1.documents:
                for doc2 in annotator2.documents:
                    if doc1.DocumentName == doc2.DocumentName and doc1.DocumentName not in done_documents:
                        interAnn.TotalOverlappingProjects = interAnn.TotalOverlappingProjects+1

                        #done_documents.append(doc1.DocumentName)
                        line_num = 0
                        ann1_objective = [0] * len(doc1.Lines)
                        ann2_objective = [0] * len(doc2.Lines)
                        ann1_output = [0] * len(doc1.Lines)
                        ann2_output = [0] * len(doc2.Lines)
                        ann1_actor = [0] * len(doc1.Lines)
                        ann2_actor = [0] * len(doc2.Lines)
                        ann1_innovativeness = [0] * len(doc1.Lines)
                        ann2_innovativeness = [0] * len(doc2.Lines)

                        # Mark_Total_Objective = 0
                        # Mark_Total_Actors = 0
                        # Mark_Total_Outputs = 0
                        # Mark_Total_Innovativeness = 0

                        if doc1.Mark_Total_Objective == doc2.Mark_Total_Objective and doc2.Mark_Total_Objective == 0:
                            count_objectives_overlap_mark0 = count_objectives_overlap_mark0+1
                        if doc1.Mark_Total_Objective == doc2.Mark_Total_Objective and doc2.Mark_Total_Objective == 1:
                            count_objectives_overlap_mark1 = count_objectives_overlap_mark1+1
                        if doc1.Mark_Total_Objective == doc2.Mark_Total_Objective and doc2.Mark_Total_Objective == 2:
                            count_objectives_overlap_mark2 = count_objectives_overlap_mark2+1
                        if doc1.Mark_Total_Objective == doc2.Mark_Total_Objective and doc2.Mark_Total_Objective == 3:
                            count_objectives_overlap_mark3 = count_objectives_overlap_mark3+1

                        if doc1.Mark_Total_Actors == doc2.Mark_Total_Actors and doc2.Mark_Total_Actors == 0:
                            count_actors_overlap_mark0 = count_actors_overlap_mark0+1
                        if doc1.Mark_Total_Actors == doc2.Mark_Total_Actors and doc2.Mark_Total_Actors == 1:
                            count_actors_overlap_mark1 = count_actors_overlap_mark1+1
                        if doc1.Mark_Total_Actors == doc2.Mark_Total_Actors and doc2.Mark_Total_Actors == 2:
                            count_actors_overlap_mark2 = count_actors_overlap_mark2+1
                        if doc1.Mark_Total_Actors == doc2.Mark_Total_Actors and doc2.Mark_Total_Actors == 3:
                            count_actors_overlap_mark3 = count_actors_overlap_mark3+1


                        if doc1.Mark_Total_Outputs == doc2.Mark_Total_Outputs and doc2.Mark_Total_Outputs == 0:
                            count_outputs_overlap_mark0 = count_outputs_overlap_mark0+1
                        if doc1.Mark_Total_Outputs == doc2.Mark_Total_Outputs and doc2.Mark_Total_Outputs == 1:
                            count_outputs_overlap_mark1 = count_outputs_overlap_mark1+1
                        if doc1.Mark_Total_Outputs == doc2.Mark_Total_Outputs and doc2.Mark_Total_Outputs == 2:
                            count_outputs_overlap_mark2 = count_outputs_overlap_mark2+1
                        if doc1.Mark_Total_Outputs == doc2.Mark_Total_Outputs and doc2.Mark_Total_Outputs == 3:
                            count_outputs_overlap_mark3 = count_outputs_overlap_mark3+1

                        if doc1.Mark_Total_Innovativeness == doc2.Mark_Total_Innovativeness and doc2.Mark_Total_Innovativeness == 0:
                            count_innovativeness_overlap_mark0 = count_innovativeness_overlap_mark0+1
                        if doc1.Mark_Total_Innovativeness == doc2.Mark_Total_Innovativeness and doc2.Mark_Total_Innovativeness == 1:
                            count_innovativeness_overlap_mark1 = count_innovativeness_overlap_mark1+1
                        if doc1.Mark_Total_Innovativeness == doc2.Mark_Total_Innovativeness and doc2.Mark_Total_Innovativeness == 2:
                            count_innovativeness_overlap_mark2 = count_innovativeness_overlap_mark2+1
                        if doc1.Mark_Total_Innovativeness == doc2.Mark_Total_Innovativeness and doc2.Mark_Total_Innovativeness == 3:
                            count_innovativeness_overlap_mark3 = count_innovativeness_overlap_mark3+1



                        if doc1.isProjectInnovativenessSatisfied == doc2.isProjectInnovativenessSatisfied:
                            interAnn.AgreementProjects_Innovativeness = interAnn.AgreementProjects_Innovativeness + 1
                            agreeing_docs_innovativeness[doc1.DocumentName] = agreeing_docs_innovativeness[doc1.DocumentName]+1
                        else:
                            fname = doc1.DocumentName
                            fcontent = doc1.Text
                            file = open(conflict_folder+"/"+fname, "w")
                            file.write(fcontent)
                            file.close()
                        if doc1.isProjectOutputSatisfied == doc2.isProjectOutputSatisfied:
                            interAnn.AgreementProjects_Outputs = interAnn.AgreementProjects_Outputs + 1
                            agreeing_docs_outputs[doc1.DocumentName] = agreeing_docs_outputs[doc1.DocumentName] + 1
                        else:
                            fname = doc1.DocumentName
                            fcontent = doc1.Text
                            file = open(conflict_folder +"/"+ fname, "w")
                            file.write(fcontent)
                            file.close()
                        if doc1.isProjectObjectiveSatisfied == doc2.isProjectObjectiveSatisfied:
                            interAnn.AgreementProjects_Objectives = interAnn.AgreementProjects_Objectives + 1
                            agreeing_docs_objectives[doc1.DocumentName] = agreeing_docs_objectives[doc1.DocumentName] + 1
                        else:
                            fname = doc1.DocumentName
                            fcontent = doc1.Text
                            file = open(conflict_folder +"/"+ fname, "w")
                            file.write(fcontent)
                            file.close()
                        if doc1.isProjectActorSatisfied == doc2.isProjectActorSatisfied:
                            interAnn.AgreementProjects_Actors = interAnn.AgreementProjects_Actors + 1
                            agreeing_docs_actors[doc1.DocumentName] = agreeing_docs_actors[doc1.DocumentName] + 1
                        else:
                            fname = doc1.DocumentName
                            fcontent = doc1.Text
                            file = open(conflict_folder +"/"+ fname, "w")
                            file.write(fcontent)
                            file.close()
                        if (doc1.isProjectActorSatisfied == doc2.isProjectActorSatisfied and doc1.isProjectObjectiveSatisfied == doc2.isProjectObjectiveSatisfied
                            and doc1.isProjectOutputSatisfied == doc2.isProjectOutputSatisfied and doc1.isProjectInnovativenessSatisfied == doc2.isProjectInnovativenessSatisfied
                            and doc1.isSpam==doc2.isSpam):
                            interAnn.AgreementSpam = interAnn.AgreementSpam + 1
                        if doc1.isSpam == doc2.isSpam:
                            interAnn.AgreementSpamSI = interAnn.AgreementSpamSI + 1

                        while line_num<len(doc1.Lines):
                            if len(doc1.Lines[line_num].Annotations)>0:
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
                            if len(doc2.Lines[line_num].Annotations)>0:
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
                        kappa_outputs = sklearn.metrics.cohen_kappa_score(ann1_output,ann2_output)
                        kappa_objectives = sklearn.metrics.cohen_kappa_score(ann1_objective, ann2_objective)
                        kappa_actors = sklearn.metrics.cohen_kappa_score(ann1_actor, ann2_actor)
                        kappa_innovativeness = sklearn.metrics.cohen_kappa_score(ann1_innovativeness, ann2_innovativeness)
                        print "Statistics for document:"+doc1.DocumentName
                        print "Annotators "+annotator1.Name+" and "+annotator2.Name
                        print "Spam by "+annotator1.Name+":"+str(doc1.isSpam)
                        print "Spam by " + annotator2.Name + ":" + str(doc2.isSpam)
                        if(doc1.isSpam == doc2.isSpam):
                            num_overlap_spam = num_overlap_spam+1
                        if doc1.isSpam:
                            num_spam = num_spam + 1
                        if doc2.isSpam:
                            num_spam = num_spam + 1
                        if doc1.isSpam_mark_based:
                            num_spam_mark_based = num_spam_mark_based + 1
                        if doc1.isSpam_mark_based:
                            num_spam_mark_based = num_spam_mark_based + 1
                        print "Cohen Kappa for class Objectives: "+str(kappa_objectives)
                        print "Cohen Kappa for class Actors: " + str(kappa_actors)
                        print "Cohen Kappa for class Outputs: " + str(kappa_outputs)
                        print "Cohen Kappa for class Innovativeness: " + str(kappa_innovativeness)
                        print "------------------------------------------------------------------"
                        kappa_files = kappa_files +1
            j = j+1
        i = i+1
        j = i+1

    for doc in agreeing_docs_objectives.keys():
        if agreeing_docs_objectives[doc]==2:
            fname = doc
            fcontent = ""
            for doca in ds.Annotators[0].documents:
                if doca.DocumentName == doc:
                    fcontent = doca.Text
            file = open(conflict_folder2 + "/" + fname, "w")
            file.write(fcontent)
            file.close()
    for doc in agreeing_docs_outputs.keys():
        if agreeing_docs_outputs[doc]==2:
            fname = doc
            fcontent = ""
            for doca in ds.Annotators[0].documents:
                if doca.DocumentName == doc:
                    fcontent = doca.Text
            file = open(conflict_folder2 + "/" + fname, "w")
            file.write(fcontent)
            file.close()
    for doc in agreeing_docs_actors.keys():
        if agreeing_docs_actors[doc]==2:
            fname = doc
            fcontent = ""
            for doca in ds.Annotators[0].documents:
                if doca.DocumentName == doc:
                    fcontent = doca.Text
            file = open(conflict_folder2 + "/" + fname, "w")
            file.write(fcontent)
            file.close()
    for doc in agreeing_docs_innovativeness.keys():
        if agreeing_docs_innovativeness[doc]==2:
            fname = doc
            fcontent = ""
            for doca in ds.Annotators[0].documents:
                if doca.DocumentName == doc:
                    fcontent = doca.Text
            file = open(conflict_folder2 + "/" + fname, "w")
            file.write(fcontent)
            file.close()

    accuracy_spam = float(num_overlap_spam)/float(kappa_files)
    print "Agreement for detecting social innovation/spam: "+str(accuracy_spam)

    print "Percentage of spam projects (in IAA set): " + str(float(num_spam)/float(2*kappa_files))
    print "Percentage of spam projects (in IAA set,mark based): " + str(float(num_spam_mark_based) / float(2 * kappa_files))
    print "Percentage of spam projects (whole set): " + str(float(total_num_spam) / float(total_num_files))
    print "Percentage of spam projects (whole set,mark based): " + str(float(total_num_spam_mark_based) / float(total_num_files))
    print ""
    print "IAA for Objectives: "+str(float(match_objectives)/float(total_objectives-match_objectives))
    print "Total and matches: "+str(total_objectives-match_objectives)+"; "+str(match_objectives)
    print "IAA for Actors: " + str(float(match_actors) / float(total_actors - match_actors))
    print "Total and matches: " + str(total_actors-match_actors) + "; " + str(match_actors)
    print "IAA for Outputs: " + str(float(match_outputs) / float(total_outputs - match_outputs))
    print "Total and matches: " + str(total_outputs-match_outputs) + "; " + str(match_outputs)
    print "IAA for Innovativeness: " + str(float(match_innovativeness) / float(total_innovativeness - match_innovativeness))
    print "Total and matches: " + str(total_innovativeness-match_innovativeness) + "; " + str(match_innovativeness)
    print "Total AII over all SL annotations: "+str(float(match_innovativeness+match_objectives+match_actors+match_outputs) / float(total_innovativeness - match_innovativeness+total_objectives-match_objectives+total_actors - match_actors+total_outputs - match_outputs))
    print "Total and matches: " + str(total_innovativeness - match_innovativeness+total_objectives-match_objectives+total_actors - match_actors+total_outputs - match_outputs) +";" +str(match_innovativeness+match_objectives+match_actors+match_outputs)
    print "IAA files count: "+str(kappa_files)

    total_objective_overlap = 0
    total_actor_overlap = 0
    total_output_overlap = 0
    total_innovativeness_overlap = 0
    total_spam_si_overlap = 0
    total_overlap = 0

    # objectives = []
    # top_actors = []
    # outputs = []
    # innovativness = []
    for ds in DocumentList:
        arr = numpy.array(ds.objectives)
        ds.objectives_sd = numpy.std(arr,axis=0)
        arr = numpy.array(ds.actors)
        ds.actors_sd = numpy.std(arr, axis=0)
        arr = numpy.array(ds.outputs)
        ds.outputs_sd = numpy.std(arr, axis=0)
        arr = numpy.array(ds.innovativness)
        ds.innovativness_sd = numpy.std(arr, axis=0)



    for annD in interAnnotatorsData:
        print "+++++++Agreement between " + annD.Annotator1 + " and " +annD.Annotator2+"+++++++"
        print "Objectives agreeing projects: "+str(annD.AgreementProjects_Objectives)+ " Total overlapping projects "+str(annD.TotalOverlappingProjects)
        total_objective_overlap = total_objective_overlap + annD.AgreementProjects_Objectives
        print "Objectives: "+str((float(annD.AgreementProjects_Objectives) /annD.TotalOverlappingProjects)*100.0)
        print "Actros agreeing projects: " + str(annD.AgreementProjects_Actors)
        total_actor_overlap = total_actor_overlap + annD.AgreementProjects_Actors
        print "Actors: " + str((float(annD.AgreementProjects_Actors) / annD.TotalOverlappingProjects)*100.0)
        print "Outputs agreeing projects: " + str(
            annD.AgreementProjects_Outputs) + " Total overlapping projects " + str(annD.TotalOverlappingProjects)
        print "Outputs: " + str((float(annD.AgreementProjects_Outputs) / annD.TotalOverlappingProjects)*100.0)
        total_output_overlap = total_output_overlap + annD.AgreementProjects_Outputs
        print "Innovativeness agreeing projects: " + str(
            annD.AgreementProjects_Innovativeness) + " Total overlapping projects " + str(annD.TotalOverlappingProjects)
        print "Innovativeness: " + str((float(annD.AgreementProjects_Innovativeness) / annD.TotalOverlappingProjects)*100.0)
        total_innovativeness_overlap = total_innovativeness_overlap + annD.AgreementProjects_Innovativeness
        print "Spam agreeing projects: " + str(
            annD.AgreementSpam) + " Total overlapping projects " + str(annD.TotalOverlappingProjects)
        total_spam_si_overlap = total_spam_si_overlap + annD.AgreementSpam
        total_overlap = total_overlap + annD.TotalOverlappingProjects
        print "Percentage of agreeing Spam over total" + str((float(annD.AgreementSpam) / annD.TotalOverlappingProjects)*100.0)
        print "Total agreeing projects: "+ str(annD.AgreementSpamSI)

    print ""
    print "Total agreements (document level):"
    print "Objectives:"+str(100.0*float(total_objective_overlap)/total_overlap)
    print "Actors:" + str(100.0 * float(total_actor_overlap) / total_overlap)
    print "Outputs:" + str(100.0 * float(total_output_overlap) / total_overlap)
    print "Innovativeness:" + str(100.0 * float(total_innovativeness_overlap) / total_overlap)
    print "Spam/SI:" + str(100.0 * float(total_spam_si_overlap) / total_overlap)

    # Annotator1 = ""
    # Annotator2 = ""
    # AgreementProjects_Objectives = 0
    # AgreementProjects_Outputs = 0
    # AgreementProjects_Actors = 0
    # AgreementProjects_Innovativeness = 0
    # TotalOverlappingProjects = 0

    kappa_total_outputs = sklearn.metrics.cohen_kappa_score(ann1_annotations_outputs, ann2_annotations_outputs)
    kappa_total_actors = sklearn.metrics.cohen_kappa_score(ann1_annotations_actors, ann2_annotations_actors)
    kappa_total_objectives = sklearn.metrics.cohen_kappa_score(ann1_annotations_objectives, ann2_annotations_objectives)
    kappa_total_innovativeness = sklearn.metrics.cohen_kappa_score(ann1_annotations_innovativeness, ann2_annotations_innovativeness)
    print ""
    print "Kappa totaly objectives: "+str(kappa_total_objectives)
    print "Kappa totaly actors: " + str(kappa_total_actors)
    print "Kappa totaly outputs: " + str(kappa_total_outputs)
    print "Kappa totaly innovativeness: " + str(kappa_total_innovativeness)

    print ""
    print "Projects with Objectives mark 0: " +str(count_objectives_mark0)
    print "Projects with Objectives mark 1: " + str(count_objectives_mark1)
    print "Projects with Objectives mark 2: " + str(count_objectives_mark2)
    print "Projects with Objectives mark 3: " + str(count_objectives_mark3)
    print "Projects with Actors mark 0: " + str(count_actors_mark0)
    print "Projects with Actors mark 1: " + str(count_actors_mark1)
    print "Projects with Actors mark 2: " + str(count_actors_mark2)
    print "Projects with Actors mark 3: " + str(count_actors_mark3)
    print "Projects with Outputs mark 0: " + str(count_outputs_mark0)
    print "Projects with Outputs mark 1: " + str(count_outputs_mark1)
    print "Projects with Outputs mark 2: " + str(count_outputs_mark2)
    print "Projects with Outputs mark 3: " + str(count_outputs_mark3)
    print "Projects with Innovativeness mark 0: " + str(count_innovativeness_mark0)
    print "Projects with Innovativeness mark 1: " + str(count_innovativeness_mark1)
    print "Projects with Innovativeness mark 2: " + str(count_innovativeness_mark2)
    print "Projects with Innovativeness mark 3: " + str(count_innovativeness_mark3)


    print ""
    print "Projects with Objectives mark overlapping 0: " +str(count_objectives_overlap_mark0)
    print "Projects with Objectives mark overlapping 1: " + str(count_objectives_overlap_mark1)
    print "Projects with Objectives mark overlapping 2: " + str(count_objectives_overlap_mark2)
    print "Projects with Objectives mark overlapping 3: " + str(count_objectives_overlap_mark3)
    print "Projects with Actors mark overlapping 0: " + str(count_actors_overlap_mark0)
    print "Projects with Actors mark overlapping 1: " + str(count_actors_overlap_mark1)
    print "Projects with Actors mark overlapping 2: " + str(count_actors_overlap_mark2)
    print "Projects with Actors mark overlapping 3: " + str(count_actors_overlap_mark3)
    print "Projects with Outputs mark overlapping 0: " + str(count_outputs_overlap_mark0)
    print "Projects with Outputs mark overlapping 1: " + str(count_outputs_overlap_mark1)
    print "Projects with Outputs mark overlapping 2: " + str(count_outputs_overlap_mark2)
    print "Projects with Outputs mark overlapping 3: " + str(count_outputs_overlap_mark3)
    print "Projects with Innovativeness mark overlapping 0: " + str(count_innovativeness_overlap_mark0)
    print "Projects with Innovativeness mark overlapping 1: " + str(count_innovativeness_overlap_mark1)
    print "Projects with Innovativeness mark overlapping 2: " + str(count_innovativeness_overlap_mark2)
    print "Projects with Innovativeness mark overlapping 3: " + str(count_innovativeness_overlap_mark3)
    print "Number of overlaps: "+str(kappa_files)
    print "Percentage of overlapping marks for Objectives: "+str(float(count_objectives_overlap_mark0+count_objectives_overlap_mark1+count_objectives_overlap_mark2+count_objectives_overlap_mark3)/float(kappa_files))
    print "Percentage of overlapping marks for Actors: " + str(float(
        count_actors_overlap_mark0 + count_actors_overlap_mark1 + count_actors_overlap_mark2 + count_actors_overlap_mark3) / float(
        kappa_files))
    print "Percentage of overlapping marks for Outputs: " + str(float(
        count_outputs_overlap_mark0 + count_outputs_overlap_mark1 + count_outputs_overlap_mark2 + count_outputs_overlap_mark3) / float(
        kappa_files))
    print "Percentage of overlapping marks for Innovativeness: " + str(float(
        count_innovativeness_overlap_mark0 + count_innovativeness_overlap_mark1 + count_innovativeness_overlap_mark2 + count_innovativeness_overlap_mark3) / float(
        kappa_files))

    top_objectives = []
    top_actors = []
    top_outputs = []
    top_innovativness = []
    top_objectives = sorted(DocumentList, key=lambda x: x.objectives_sd, reverse=True)
    top_actors = sorted(DocumentList, key=lambda x: x.actors_sd, reverse=True)
    top_outputs = sorted(DocumentList, key=lambda x: x.outputs_sd, reverse=True)
    top_innovativness = sorted(DocumentList, key=lambda x: x.innovativness_sd, reverse=True)

    print ""
    print "List of files by SD from objectives perspective:"
    a = 0
    for f in top_objectives:
        if a>=10:
            continue
        print f.Name+"   "+str(f.objectives_sd)+"   marks:"+str(f.objectives)
        a = a+1
    print ""
    print "List of files by SD from actors perspective:"
    a = 0
    for f in top_actors:
        if a>=10:
            continue
        print f.Name + "   " + str(f.actors_sd)+"   marks:"+str(f.actors)
        a = a+1
    print ""
    print "List of files by SD from outputs perspective:"
    a = 0
    for f in top_outputs:
        if a>=10:
            continue
        print f.Name + "   " + str(f.outputs_sd)+"   marks:"+str(f.outputs)
        a = a+1
    print ""
    print "List of files by SD from innovativness perspective:"
    a = 0
    for f in top_innovativness:
        if a>=10:
            continue
        print f.Name + "   " + str(f.innovativness_sd)+"   marks:"+str(f.innovativness)
        a = a+1

    datasources = {}
    spam_per_datasource = {}
    for ann in dataset.Annotators:
        for doc in ann.documents:
            if doc.FromDataset in datasources:
                datasources[doc.FromDataset] = datasources[doc.FromDataset] + 1
            else:
                datasources[doc.FromDataset] = 1
            if doc.FromDataset in spam_per_datasource and doc.isSpam:
                spam_per_datasource[doc.FromDataset] = spam_per_datasource[doc.FromDataset] + 1
            elif doc.FromDataset not in spam_per_datasource and doc.isSpam:
                spam_per_datasource[doc.FromDataset] =  1
    print ""
    print "Total documents per datasource"
    for key in datasources:
        print key + ": "+str(datasources[key])
    print ""
    print "Total spam documents per datasource"
    for key in spam_per_datasource:
        print key + ": " + str(spam_per_datasource[key])



