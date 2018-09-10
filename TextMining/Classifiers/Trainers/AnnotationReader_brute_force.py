import csv
from os import listdir
from os.path import isfile, join

class AnnotatedFile:
    def __init__(self):
        self.file_name = ""
        self.Objectives = -1
        self.Actors = -1
        self.Outputs = -1
        self.Innovativeness = -1
        self.SocialInnovation = -1

annotator1_path = "../../../Helpers/SI_dataset/Ann1"
annotator2_path = "../../../Helpers/SI_dataset/Ann2"
conflicts_path = "../../../Helpers/SI_dataset/Conflicts"

ann1files = [f for f in listdir(annotator1_path) if isfile(join(annotator1_path, f))]
ann2files = [f for f in listdir(annotator2_path) if isfile(join(annotator2_path, f))]
conflictsfiles = [f for f in listdir(conflicts_path) if isfile(join(conflicts_path, f))]

annotated1_docs = []
annotated2_docs = []
conflicts_docs = []

for ann in ann1files:
    if ".ann" not in ann:
        continue
    f = open(annotator1_path+"/"+ann,"r")
    lines = f.readlines()
    a = AnnotatedFile()
    a.file_name = ann
    for line in lines:
        line = line.replace('\n','')
        if "DL_Actors" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Actors = int(parts[2])
        if "DL_SocialInnovation" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.SocialInnovation = int(parts[2])
        if "DL_Innovativeness" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Innovativeness = int(parts[2])
        if "DL_Objective" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Objectives = int(parts[2])
        if "DL_Outputs" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Outputs = int(parts[2])
    annotated1_docs.append(a)

for ann in ann2files:
    if ".ann" not in ann:
        continue
    f = open(annotator2_path+"/"+ann,"r")
    lines = f.readlines()
    a = AnnotatedFile()
    a.file_name = ann
    for line in lines:
        line = line.replace('\n', '')
        if "DL_Actors" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Actors = int(parts[2])
        if "DL_SocialInnovation" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.SocialInnovation = int(parts[2])
        if "DL_Innovativeness" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Innovativeness = int(parts[2])
        if "DL_Objective" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Objectives = int(parts[2])
        if "DL_Outputs" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Outputs = int(parts[2])
    annotated2_docs.append(a)

for ann in conflictsfiles:
    if ".ann" not in ann:
        continue
    f = open(conflicts_path+"/"+ann,"r")
    lines = f.readlines()
    a = AnnotatedFile()
    a.file_name = ann
    for line in lines:
        line = line.replace('\n', '')
        if "DL_Actors" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Actors = int(parts[2])
        if "DL_SocialInnovation" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.SocialInnovation = int(parts[2])
        if "DL_Innovativeness" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Innovativeness = int(parts[2])
        if "DL_Objective" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Objectives = int(parts[2])
        if "DL_Outputs" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Outputs = int(parts[2])
    conflicts_docs.append(a)
csv_file = open('annotations2.csv','wb')
writer = csv.writer(csv_file,quotechar='"',quoting=csv.QUOTE_MINIMAL)
writer.writerow(['Doc','Objectives1','Actors1','Outputs1','Innovativeness1','SI1','Objectives2','Actors2','Outputs2',
                 'Innovativeness2','SI2','Objectives_c','Actors_c','Outputs_c','Innovativeness_c','SI_c'])

for ann1 in annotated1_docs:
    doc = ""
    objectives1 = -1
    actors1 = -1
    outputs1 = -1
    innovativeness1 = -1
    SI1 = -1
    objectives2 = -1
    actors2 = -1
    outputs2 = -1
    innovativeness2 = -1
    SI2 = -1
    objectives_c = -1
    actors_c = -1
    outputs_c = -1
    innovativeness_c = -1
    SI_c = -1
    for ann2 in annotated2_docs:
        if ann1.file_name == ann2.file_name:
            doc = ann1.file_name
            objectives1 = ann1.Objectives
            actors1 = ann1.Actors
            outputs1 = ann1.Outputs
            innovativeness1 = ann1.Innovativeness
            SI1 = ann1.SocialInnovation

            objectives2 = ann2.Objectives
            actors2 = ann2.Actors
            outputs2 = ann2.Outputs
            innovativeness2 = ann2.Innovativeness
            SI2 = ann2.SocialInnovation
    for ann_c in conflicts_docs:
        if ann1.file_name == ann_c.file_name:
            objectives_c = ann_c.Objectives
            actors_c = ann_c.Actors
            outputs_c = ann_c.Outputs
            innovativeness_c = ann_c.Innovativeness
            SI_c = ann_c.SocialInnovation
    writer.writerow([doc,objectives1,actors1,outputs1,innovativeness1,SI1,objectives2,actors2,outputs2,innovativeness2,SI2,objectives_c,
                     actors_c,outputs_c,innovativeness_c,SI_c])
csv_file.close()





