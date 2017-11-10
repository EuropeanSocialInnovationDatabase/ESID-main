import nltk
from os import listdir
from os.path import isfile, join,isdir
import csv
import re
import sklearn.metrics
import os
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

if __name__ == '__main__':
    data_folder = "../FullDataset_Alina"
    ds = DataSet()
    total_num_spam = 0
    total_num_files = 0
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
            doc.DocumentName= file
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
                    if(low_level_ann == "SL_Outputs_3a"):
                        Ann.HighLevelClass = "Outputs"
                    if (low_level_ann == "SL_Objective_1a" or low_level_ann == "SL_Objective_1b" or low_level_ann == "SL_Objective_1c"):
                        Ann.HighLevelClass = "Objectives"
                    if (low_level_ann == "SL_Actors_2a" or low_level_ann == "SL_Actors_2b" or low_level_ann == "SL_Actors_2c"):
                        Ann.HighLevelClass = "Actors"
                    if (low_level_ann == "SL_Innovativeness_4a"):
                        Ann.HighLevelClass = "Innovativeness"
                    doc.Annotations.append(Ann)
                    for line in doc.Lines:
                        if line.StartSpan<=Ann.StartSpan and line.EndSpan>=Ann.EndSpan:
                            line.Annotations.append(Ann)
                else:
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
            if(doc.Project_Mark_Objective_1A==0 and doc.Project_Mark_Objective_1B == 0 and doc.Project_Mark_Objective_1C==0 and doc.Project_Mark_Actors_2A==0
                and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2C==0 and doc.Project_Mark_Outputs_3A == 0
                and doc.Project_Mark_Innovativeness_3A==0):
                doc.isSpam = True
                total_num_spam = total_num_spam + 1

    with open('annotations.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        for ann in ds.Annotators:
            for doc in ann.documents:
                for annot in doc.Annotations:
                    spamwriter.writerow([annot.FromFile,annot.FromAnnotator,annot.AnnotationText,annot.LowLevelClass,annot.HighLevelClass,annot.StartSpan,annot.EndSpan])
    i = 0
    j = i+1
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
    while i<len(ds.Annotators)-1:
        while j<len(ds.Annotators):
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
                        print "Cohen Kappa for class Objectives: "+str(kappa_objectives)
                        print "Cohen Kappa for class Actors: " + str(kappa_actors)
                        print "Cohen Kappa for class Outputs: " + str(kappa_outputs)
                        print "Cohen Kappa for class Innovativeness: " + str(kappa_innovativeness)
                        print "------------------------------------------------------------------"
                        kappa_files = kappa_files +1
            j = j+1
        i = i+1
        j = i+1

    # accuracy_spam = float(num_overlap_spam)/float(kappa_files)
    # print "Agreement for detecting social innovation/spam: "+str(accuracy_spam)
    # print "Percentage of spam projects (in IAA set): " + str(float(num_spam)/float(2*kappa_files))
    # print "Percentage of spam projects (whole set): " + str(float(total_num_spam) / float(total_num_files))
    # print ""
    # print "IAA for Objectives: "+str(float(match_objectives)/float(total_objectives-match_objectives))
    # print "Total and matches: "+str(total_objectives-match_objectives)+"; "+str(match_objectives)
    # print "IAA for Actors: " + str(float(match_actors) / float(total_actors - match_actors))
    # print "Total and matches: " + str(total_actors-match_actors) + "; " + str(match_actors)
    # print "IAA for Outputs: " + str(float(match_outputs) / float(total_outputs - match_outputs))
    # print "Total and matches: " + str(total_outputs-match_outputs) + "; " + str(match_outputs)
    # print "IAA for Innovativeness: " + str(float(match_innovativeness) / float(total_innovativeness - match_innovativeness))
    # print "Total and matches: " + str(total_innovativeness-match_innovativeness) + "; " + str(match_innovativeness)
    # print "Total AII over all SL annotations: "+str(float(match_innovativeness+match_objectives+match_actors+match_outputs) / float(total_innovativeness - match_innovativeness+total_objectives-match_objectives+total_actors - match_actors+total_outputs - match_outputs))
    # print "Total and matches: " + str(total_innovativeness - match_innovativeness+total_objectives-match_objectives+total_actors - match_actors+total_outputs - match_outputs) +";" +str(match_innovativeness+match_objectives+match_actors+match_outputs)
    # print "IAA files count: "+str(kappa_files)
    # kappa_total_outputs = sklearn.metrics.cohen_kappa_score(ann1_annotations_outputs, ann2_annotations_outputs)
    # kappa_total_actors = sklearn.metrics.cohen_kappa_score(ann1_annotations_actors, ann2_annotations_actors)
    # kappa_total_objectives = sklearn.metrics.cohen_kappa_score(ann1_annotations_objectives, ann2_annotations_objectives)
    # kappa_total_innovativeness = sklearn.metrics.cohen_kappa_score(ann1_annotations_innovativeness, ann2_annotations_innovativeness)
    # print ""
    # print "Kappa totaly objectives: "+str(kappa_total_objectives)
    # print "Kappa totaly actors: " + str(kappa_total_actors)
    # print "Kappa totaly outputs: " + str(kappa_total_outputs)
    # print "Kappa totaly innovativeness: " + str(kappa_total_innovativeness)

    print annotators
    doc_array = []
    for ann in ds.Annotators:
        for doc in ann.documents:
            doc_array.append([doc.Text,doc.isProjectObjectiveSatisfied,doc.isProjectActorSatisfied,doc.isProjectOutputSatisfied,doc.isProjectInnovativenessSatisfied,doc.DocumentName])

    data_x = []
    data_y = []
    test_x = []
    test_y = []
    directory1 = "Good"
    directory2 = "Bad"
    if not os.path.exists(directory1):
        os.makedirs(directory1)
    if not os.path.exists(directory2):
        os.makedirs(directory2)
    for x in doc_array:
        data_x.append(x[0])
        data_y.append(x[3])
        if x[3]== True:
            file = open(directory1+"/"+x[5],"w")
            file.write(x[0])
            file.close()
        else:
            file = open(directory2 + "/" + x[5],"w")
            file.write(x[0])
            file.close()





