# MLP for Pima Indians Dataset Serialize to JSON and HDF5
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy
from os import listdir
from os.path import isfile,join
import os
import sys
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding
sys.path.insert(0, '../Statistics/')
sys.path.insert(0, '../Trainers/')
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import re
from os.path import isfile, join,isdir
from ANN_Trainer_Actors import DataSet,Annotator,Document,Line,Annotation

from Measures import *
max_words = 20000
batch_size = 32
MAX_SEQUENCE_LENGTH = 1100
json_file_actor = open('../Models/model_actors.json', 'r')
json_file_objectives = open('../Models/model_objectives.json', 'r')
json_file_outputs = open('../Models/model_outputs.json', 'r')
json_file_innovativeness = open('../Models/model_innovativeness.json', 'r')
loaded_model_actor_json = json_file_actor.read()
loaded_model_objectives_json = json_file_objectives.read()
loaded_model_outputs_json = json_file_outputs.read()
loaded_model_innovativeness_json = json_file_innovativeness.read()
json_file_actor.close()
json_file_objectives.close()
json_file_outputs.close()
json_file_innovativeness.close()
loaded_model_actor = model_from_json(loaded_model_actor_json)
loaded_model_objectives = model_from_json(loaded_model_objectives_json)
loaded_model_outputs = model_from_json(loaded_model_outputs_json)
loaded_model_innovativeness = model_from_json(loaded_model_innovativeness_json)
# load weights into new model
loaded_model_actor.load_weights("../Models/model_actors.h5")
loaded_model_objectives.load_weights("../Models/model_objectives.h5")
loaded_model_outputs.load_weights("../Models/model_outputs.h5")
loaded_model_innovativeness.load_weights("../Models/model_innovativeness.h5")
print("Loaded model from disk")
EMBEDDING_DIM = 50



# evaluate loaded model on test data
#loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
loaded_model_actor.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_objectives.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_outputs.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
loaded_model_innovativeness.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',mcor,precision,recall, f1])
data_folder = "../../../Helpers/FullDataset_Alina/"
onlyfiles = [f for f in listdir(data_folder) if isfile(join(data_folder,f))]




###############################################################
ds = DataSet()
total_num_spam = 0
sentences = []
total_num_files = 0
#job = aetros.backend.start_job('nikolamilosevic86/GloveModel')
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
            sentences.append(line)
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
                    if(doc1.isSpam == doc2.isSpam):
                        num_overlap_spam = num_overlap_spam+1
                    if doc1.isSpam:
                        num_spam = num_spam + 1
                    if doc2.isSpam:
                        num_spam = num_spam + 1
                    print "------------------------------------------------------------------"
                    kappa_files = kappa_files +1
        j = j+1
    i = i+1
    j = i+1

print annotators
doc_array = []
text_array = []
objectives = []
actors = []
outputs = []
innovativeness = []
for ann in ds.Annotators:
    for doc in ann.documents:
        doc_array.append([doc.Text,doc.isProjectObjectiveSatisfied,doc.isProjectActorSatisfied,doc.isProjectOutputSatisfied,doc.isProjectInnovativenessSatisfied])
        objectives.append(doc.isProjectObjectiveSatisfied)
        actors.append(doc.isProjectActorSatisfied)
        outputs.append(doc.isProjectOutputSatisfied)
        innovativeness.append(doc.isProjectInnovativenessSatisfied)
        text_array.append(doc.Text)
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(text_array)
sequences = tokenizer.texts_to_sequences(text_array)

word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))

data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

labels = to_categorical(np.asarray(actors))
print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', labels.shape)

# split the data into a training set and a validation set
indices = np.arange(data.shape[0])
data = data[indices]
labels = labels[indices]
x_train = data
y_train = labels


##############################################################


        #early_stopping = EarlyStopping(monitor='val_loss', patience=15)
print "Actor"
predictions_actor = loaded_model_actor.predict(x_train,batch_size,1)
i = 0
for pred in predictions_actor:
    print str(file) +": "+str(pred)
    i = i+1
print "Objectives"
predictions_objectives = loaded_model_objectives.predict(x_train,batch_size,1)
i = 0
for pred in predictions_objectives:
    print str(file) + ": " + str(pred)
    i = i + 1
print "Outputs"
predictions_outputs = loaded_model_outputs.predict(x_train,batch_size,1)
i = 0
for pred in predictions_outputs:
    print str(file) + ": " + str(pred)
    i = i + 1
print "Innovativeness"
predictions_innovativeness = loaded_model_innovativeness.predict(x_train,batch_size,1)
i = 0
for pred in predictions_innovativeness:
    print str(file) + ": " + str(pred)
    i = i + 1
