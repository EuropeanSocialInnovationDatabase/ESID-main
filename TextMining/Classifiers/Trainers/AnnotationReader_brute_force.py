import csv
from os import listdir
from os.path import isfile, join
import os
from shutil import copyfile

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
        if "SpamProject" in line:
            a.Actors = 0
            a.SocialInnovation = 0
            a.Innovativeness = 0
            a.Objectives = 0
            a.Outputs = 0
            continue
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
        if "SpamProject" in line:
            a.Actors = 0
            a.SocialInnovation = 0
            a.Innovativeness = 0
            a.Objectives = 0
            a.Outputs = 0
            continue
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
        if "SpamProject" in line:
            a.Actors = 0
            a.SocialInnovation = 0
            a.Innovativeness = 0
            a.Objectives = 0
            a.Outputs = 0
            continue
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
                 'Innovativeness2','SI2','Objectives_c','Actors_c','Outputs_c','Innovativeness_c','SI_c','final_Objectives','final_Actors','final_Outputs','final_Innovativeness','final_SI'])
spam_projects = []
si_marked = []
si_dataset = "../../../Helpers/SI_dataset/Output/SI_only"
whole_dataset = "../../../Helpers/SI_dataset/Output/SI_data_ZSI_final"
if not os.path.exists(si_dataset):
    os.makedirs(si_dataset)
if not os.path.exists(whole_dataset):
    os.makedirs(whole_dataset)
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
    f_objectives = -1
    f_actors = -1
    f_outputs = -1
    f_innovativeness = -1
    f_SI = -1
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

    if objectives_c == -1:
        f_objectives = int(round((objectives1 + objectives2) / 2.0))
        f_outputs = int(round((outputs1 + outputs2) / 2.0))
        f_actors = int(round((actors1 + actors2) / 2.0))
        f_innovativeness = int(round((innovativeness1+innovativeness2)/2.0))
        doc_path = annotator1_path + "/"+doc.replace('.ann','.txt')
        copyfile(doc_path,whole_dataset+"/"+doc.replace('.ann','.txt'))
        fa = open(whole_dataset+'/'+doc,'w')
        fa.write("Objectives: "+str(f_objectives)+'\r\n')
        fa.write("Actors: " + str(f_actors)+'\r\n')
        fa.write("Outputs: " + str(f_outputs) + '\r\n')
        fa.write("Innovativenss: " + str(f_innovativeness) + '\r\n')
        if SI1 != -1 and SI2!=-1:

            f_SI = int(round((SI1 + SI2)/2.0))
            copyfile(doc_path, si_dataset + "/" + doc.replace('.ann', '.txt'))
            sif = open(si_dataset + "/" + doc, 'w')
            sif.write("Objectives: " + str(f_objectives) + '\r\n')
            sif.write("Actors: " + str(f_actors) + '\r\n')
            sif.write("Outputs: " + str(f_outputs) + '\r\n')
            sif.write("Innovativenss: " + str(f_innovativeness) + '\r\n')
            sif.write("SI: " + str(f_SI) + '\r\n')
            sif.close()
            fa.write("SI: " + str(f_SI) + '\r\n')
            si_marked.append(doc)
        fa.close()
    else:
        f_objectives = int(round((objectives1 + objectives2+objectives_c) / 3.0))
        f_outputs = int(round((outputs1 + outputs2 + outputs_c) / 3.0))
        f_actors = int(round((actors1 + actors2 + actors_c) / 3.0))
        f_innovativeness = int(round((innovativeness1 + innovativeness2 + innovativeness_c) / 3.0))
        doc_path = annotator1_path + "/" + doc.replace('.ann', '.txt')
        copyfile(doc_path, whole_dataset + "/" + doc.replace('.ann', '.txt'))
        fa = open(whole_dataset + '/' + doc, 'w')
        fa.write("Objectives: " + str(f_objectives) + '\r\n')
        fa.write("Actors: " + str(f_actors) + '\r\n')
        fa.write("Outputs: " + str(f_outputs) + '\r\n')
        fa.write("Innovativenss: " + str(f_innovativeness) + '\r\n')
        if SI1 != -1 and SI2 != -1 and SI_c!=-1:
            f_SI = int(round((SI1 + SI2 + SI_c) / 3.0))
            copyfile(doc_path, si_dataset + "/" + doc.replace('.ann', '.txt'))
            sif = open(si_dataset + "/" + doc, 'w')
            sif.write("Objectives: " + str(f_objectives) + '\r\n')
            sif.write("Actors: " + str(f_actors) + '\r\n')
            sif.write("Outputs: " + str(f_outputs) + '\r\n')
            sif.write("Innovativenss: " + str(f_innovativeness) + '\r\n')
            sif.write("SI: " + str(f_SI) + '\r\n')
            sif.close()
            fa.write("SI: " + str(f_SI) + '\r\n')
            si_marked.append(doc)
        fa.close()
    if f_objectives + f_outputs + f_innovativeness + f_actors < 4:
        spam_projects.append(doc)
        copyfile(doc_path, si_dataset + "/" + doc.replace('.ann', '.txt'))
        sif = open(si_dataset + "/" + doc, 'w')
        sif.write("Objectives: " + str(f_objectives) + '\r\n')
        sif.write("Actors: " + str(f_actors) + '\r\n')
        sif.write("Outputs: " + str(f_outputs) + '\r\n')
        sif.write("Innovativenss: " + str(f_innovativeness) + '\r\n')
        sif.write("SI: 0"  + '\r\n')
        sif.close()

    writer.writerow(
        [doc, objectives1, actors1, outputs1, innovativeness1, SI1, objectives2, actors2, outputs2, innovativeness2,
         SI2, objectives_c,
         actors_c, outputs_c, innovativeness_c, SI_c,f_objectives,f_actors,f_outputs,f_innovativeness,f_SI])
print("SI marked:"+str(len(si_marked)))
print("Spam:"+str(len(spam_projects)))

csv_file.close()





