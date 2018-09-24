import csv
from os import listdir
from os.path import isfile, join
import os
from shutil import copyfile

class AnnotatedFile:
    def __init__(self):
        self.file_name = ""
        self.Objectives = 0
        self.Actors = 0
        self.Outputs = 0
        self.Innovativeness = 0
        self.SocialInnovation = -1

annotator1_path = "../../../Helpers/FullDataset_Alina/Ann1"


ann1files = [f for f in listdir(annotator1_path) if isfile(join(annotator1_path, f))]

annotated1_docs = []


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
            potential = int(parts[2])
            if potential>a.Actors:
                a.Actors = potential
        if "DL_SocialInnovation" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')

            potential = int(parts[2])
            if potential > a.SocialInnovation:
                a.SocialInnovation = potential
        if "DL_Innovativeness" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            a.Innovativeness = int(parts[2])
            potential = int(parts[2])
            if potential > a.Innovativeness:
                a.Innovativeness = potential
        if "DL_Objective" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            potential = int(parts[2])
            if potential > a.Objectives:
                a.Objectives = potential
        if "DL_Outputs" in line:
            parts = line.split("\t")
            parts = parts[1].split(' ')
            potential = int(parts[2])
            if potential > a.Outputs:
                a.Outputs = potential
    annotated1_docs.append(a)

whole_dataset = "../../../Helpers/SI_dataset/Output/SI_data_Alina_final"
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
    doc = ann1.file_name
    if "swp" in doc:
        continue
    doc_path = annotator1_path + "/"+doc.replace('.ann','.txt')
    copyfile(doc_path,whole_dataset+"/"+doc.replace('.ann','.txt'))
    fa = open(whole_dataset+'/'+doc,'w')
    fa.write("Objectives: "+str(ann1.Objectives)+'\r\n')
    fa.write("Actors: " + str(ann1.Actors)+'\r\n')
    fa.write("Outputs: " + str(ann1.Outputs) + '\r\n')
    fa.write("Innovativenss: " + str(ann1.Innovativeness) + '\r\n')


    fa.close()







