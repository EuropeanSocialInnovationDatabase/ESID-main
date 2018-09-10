import csv

from bratreader.repomodel import RepoModel

annotator1_path = "../../../Helpers/SI_dataset/Ann1"
annotator2_path = "../../../Helpers/SI_dataset/Ann2"
conflicts_path = "../../../Helpers/SI_dataset/Conflicts"
r1 = RepoModel(annotator1_path)
r2 = RepoModel(annotator2_path)
cr = RepoModel(conflicts_path)
print(len(r1.documents))

doc_count = 0
DL_Actors_total = 0
DL_Innovativeness_total = 0
DL_Objective_total = 0
DL_Outputs_total = 0
DL_SocialInnovation_total = 0
directory = "../../../Helpers/SI_Consolidated_dataset/"
import os
if not os.path.exists(directory):
    os.makedirs(directory)

frequency_0_ann1_Actors = 0
frequency_1_ann1_Actors = 0
frequency_2_ann1_Actors = 0
frequency_3_ann1_Actors = 0
frequency_0_ann2_Actors = 0
frequency_1_ann2_Actors = 0
frequency_2_ann2_Actors = 0
frequency_3_ann2_Actors = 0

frequency_0_ann1_Objectives = 0
frequency_1_ann1_Objectives = 0
frequency_2_ann1_Objectives = 0
frequency_3_ann1_Objectives = 0

frequency_0_ann2_Objectives = 0
frequency_1_ann2_Objectives = 0
frequency_2_ann2_Objectives = 0
frequency_3_ann2_Objectives = 0

frequency_0_ann1_Outputs = 0
frequency_1_ann1_Outputs = 0
frequency_2_ann1_Outputs = 0
frequency_3_ann1_Outputs = 0

frequency_0_ann2_Outputs = 0
frequency_1_ann2_Outputs = 0
frequency_2_ann2_Outputs = 0
frequency_3_ann2_Outputs = 0

frequency_0_ann1_Innovativeness = 0
frequency_1_ann1_Innovativeness = 0
frequency_2_ann1_Innovativeness = 0
frequency_3_ann1_Innovativeness = 0

frequency_0_ann2_Innovativeness = 0
frequency_1_ann2_Innovativeness = 0
frequency_2_ann2_Innovativeness = 0
frequency_3_ann2_Innovativeness = 0

frequency_0_ann1_SI = 0
frequency_1_ann1_SI = 0
frequency_2_ann1_SI = 0
frequency_3_ann1_SI = 0

frequency_0_ann2_SI = 0
frequency_1_ann2_SI = 0
frequency_2_ann2_SI = 0
frequency_3_ann2_SI = 0

Objectives_exact_match = 0
Actors_exact_match = 0
Outputs_exact_match = 0
Innovativeness_exact_match = 0
SI_exact_match = 0

Objectives_1diff = 0
Actors_1diff = 0
Outputs_1diff = 0
Innovativeness_1diff = 0
SI_1diff = 0

Objectives_2diff = 0
Actors_2diff = 0
Outputs_2diff = 0
Innovativeness_2diff = 0
SI_2diff = 0

Objectives_3diff = 0
Actors_3diff = 0
Outputs_3diff = 0
Innovativeness_3diff = 0
SI_3diff = 0

csv_file = open('annotations.csv','wb')
writer = csv.writer(csv_file,quotechar='"',quoting=csv.QUOTE_MINIMAL)
writer.writerow(['Doc','Objectives1','Actors1','Outputs1','Innovativeness1','SI1','Objectives2','Actors2','Outputs2','Innovativeness2','SI2'])
for doc in r1.documents:
    #print(doc)
    document = r1.documents[doc]
    document_content = ''
    DL_Outputs1 = -1
    DL_Outputs2 = -1
    DL_Objective1 = -1
    DL_Objective2 = -1
    DL_SocialInnovation1 = -1
    DL_SocialInnovation2 = -1
    DL_Innovativeness1 = -1
    DL_Innovativeness2 = -1
    DL_Actors1 = -1
    DL_Actors2 = -1

    for annotation in document.annotations:
        if "SpamProject" in annotation.labels.keys():
            DL_Outputs1 = 0
            DL_Actors1 = 0
            DL_Objective1 = 0
            DL_Innovativeness1 = 0
            DL_SocialInnovation1 = 0
        if "DL_Actors" in annotation.labels.keys() and len(annotation.labels['DL_Actors'])>0:
            DL_Actors1 = int(annotation.labels['DL_Actors'][0])

        if "DL_Innovativeness" in annotation.labels.keys():
            DL_Innovativeness1 = int(annotation.labels['DL_Innovativeness'][0])

        if "DL_Objective" in annotation.labels.keys():
            DL_Objective1 = int(annotation.labels['DL_Objective'][0])

        if "DL_Outputs" in annotation.labels.keys():
            DL_Outputs1 = int(annotation.labels['DL_Outputs'][0])

        if "DL_SocialInnovation" in annotation.labels.keys():
            DL_SocialInnovation1 = int(annotation.labels['DL_SocialInnovation'][0])

    if DL_Actors1 == 0:
        frequency_0_ann1_Actors = frequency_0_ann1_Actors + 1
    if DL_Actors1 == 1:
        frequency_1_ann1_Actors = frequency_1_ann1_Actors + 1
    if DL_Actors1 == 2:
        frequency_2_ann1_Actors = frequency_2_ann1_Actors + 1
    if DL_Actors1 == 3:
        frequency_3_ann1_Actors = frequency_3_ann1_Actors + 1
    if DL_Innovativeness1 == 0:
        frequency_0_ann1_Innovativeness = frequency_0_ann1_Innovativeness + 1
    if DL_Innovativeness1 == 1:
        frequency_1_ann1_Innovativeness = frequency_1_ann1_Innovativeness + 1
    if DL_Innovativeness1 == 2:
        frequency_2_ann1_Innovativeness = frequency_2_ann1_Innovativeness + 1
    if DL_Innovativeness1 == 3:
        frequency_3_ann1_Innovativeness = frequency_3_ann1_Innovativeness + 1
    if DL_Objective1 == 0:
        frequency_0_ann1_Objectives = frequency_0_ann1_Objectives + 1
    if DL_Objective1 == 1:
        frequency_1_ann1_Objectives = frequency_1_ann1_Objectives + 1
    if DL_Objective1 == 2:
        frequency_2_ann1_Objectives = frequency_2_ann1_Objectives + 1
    if DL_Objective1 == 3:
        frequency_3_ann1_Objectives = frequency_3_ann1_Objectives + 1
    if DL_Outputs1 == 0:
        frequency_0_ann1_Outputs = frequency_0_ann1_Outputs + 1
    if DL_Outputs1 == 1:
        frequency_1_ann1_Outputs = frequency_1_ann1_Outputs + 1
    if DL_Outputs1 == 2:
        frequency_2_ann1_Outputs = frequency_2_ann1_Outputs + 1
    if DL_Outputs1 == 3:
        frequency_3_ann1_Outputs = frequency_3_ann1_Outputs + 1
    if DL_SocialInnovation1 == 0:
        frequency_0_ann1_SI = frequency_0_ann1_SI + 1
    if DL_SocialInnovation1 == 1:
        frequency_1_ann1_SI = frequency_1_ann1_SI + 1
    if DL_SocialInnovation1 == 2:
        frequency_2_ann1_SI = frequency_2_ann1_SI + 1
    if DL_SocialInnovation1 == 3:
        frequency_3_ann1_SI = frequency_3_ann1_SI + 1
    document2 = r2.documents[doc]
    for annotation2 in document2.annotations:
        if "SpamProject" in annotation2.labels.keys():
            DL_Outputs2 = 0
            DL_Actors2 = 0
            DL_Objective2 = 0
            DL_Innovativeness2 = 0
            DL_SocialInnovation2 = 0
        if "DL_Actors" in annotation2.labels.keys():
            DL_Actors2 = int(annotation2.labels['DL_Actors'][0])
        if "DL_Innovativeness" in annotation2.labels.keys():
            DL_Innovativeness2 = int(annotation2.labels['DL_Innovativeness'][0])
        if "DL_Objective" in annotation2.labels.keys():
            DL_Objective2 = int(annotation2.labels['DL_Objective'][0])
        if "DL_Outputs" in annotation2.labels.keys():
            DL_Outputs2 = int(annotation2.labels['DL_Outputs'][0])
        if "DL_SocialInnovation" in annotation2.labels.keys():
            DL_SocialInnovation2 = int(annotation2.labels['DL_SocialInnovation'][0])

    if DL_Actors1!=-1 and DL_Actors2!=-1:
        if DL_Actors1==DL_Actors2:
            Actors_exact_match = Actors_exact_match + 1
            Actors_exact_match = Actors_exact_match + 1
        if abs(DL_Actors2 - DL_Actors1) == 1:
            Actors_1diff = Actors_1diff + 1
        if abs(DL_Actors2 - DL_Actors1) == 2:
            Actors_2diff = Actors_2diff + 1
        if abs(DL_Actors2 - DL_Actors1) == 3:
            Actors_3diff = Actors_3diff + 1
    if DL_Objective1 != -1 and DL_Objective2 != -1:
        if DL_Objective1==DL_Objective2:
            Objectives_exact_match = Objectives_exact_match + 1
        if abs(DL_Objective2 - DL_Objective1) == 1:
            Objectives_1diff = Objectives_1diff + 1
        if abs(DL_Objective2 - DL_Objective1) == 2:
            Objectives_2diff = Objectives_2diff + 1
        if abs(DL_Objective2 - DL_Objective2) == 3:
            Objectives_3diff = Objectives_3diff + 1
    else:
        print('Error with:'+doc)
    if DL_Outputs1 != -1 and DL_Outputs2 != -1:
        if DL_Outputs1 == DL_Outputs2:
            Outputs_exact_match = Outputs_exact_match + 1
        if abs(DL_Outputs2 - DL_Outputs1) == 1:
            Outputs_1diff = Outputs_1diff + 1
        if abs(DL_Outputs2 - DL_Outputs1) == 2:
            Outputs_2diff = Outputs_2diff + 1
        if abs(DL_Outputs2 - DL_Outputs1) == 3:
            Outputs_3diff = Outputs_3diff + 1
    if DL_Innovativeness1 != -1 and DL_Innovativeness2 != -1:
        if DL_Innovativeness1 == DL_Innovativeness2:
            Innovativeness_exact_match = Innovativeness_exact_match + 1
        if abs(DL_Innovativeness2 - DL_Innovativeness1) == 1:
            Innovativeness_1diff = Innovativeness_1diff + 1
        if abs(DL_Innovativeness2 - DL_Innovativeness1) == 2:
            Innovativeness_2diff = Innovativeness_2diff + 1
        if abs(DL_Innovativeness2 - DL_Innovativeness1) == 3:
            Innovativeness_3diff = Innovativeness_3diff + 1
    if DL_SocialInnovation1 != -1 and DL_SocialInnovation2 != -1:
        if DL_SocialInnovation1 == DL_SocialInnovation2:
            SI_exact_match = SI_exact_match + 1
        if abs(DL_SocialInnovation2-DL_SocialInnovation1)==1:
            SI_1diff = SI_1diff + 1
        if abs(DL_SocialInnovation2-DL_SocialInnovation1)==2:
            SI_2diff = SI_2diff + 1
        if abs(DL_SocialInnovation2-DL_SocialInnovation1)==3:
            SI_3diff = SI_3diff + 1
    writer.writerow([doc,DL_Objective1,DL_Actors1,DL_Outputs1,DL_Innovativeness1,DL_SocialInnovation1,DL_Objective2,DL_Actors2,DL_Outputs2,DL_Innovativeness2,DL_SocialInnovation2])



for doc2 in r2.documents:
    document2 = r2.documents[doc2]
    for annotation in document2.annotations:
        if "DL_Actors" in annotation.labels.keys():
            DL_Actors2 = int(annotation.labels['DL_Actors'][0])
        if "DL_Innovativeness" in annotation.labels.keys():
            DL_Innovativeness2 = int(annotation.labels['DL_Innovativeness'][0])
        if "DL_Objective" in annotation.labels.keys():
            DL_Objective2 = int(annotation.labels['DL_Objective'][0])
        if "DL_Outputs" in annotation.labels.keys():
            DL_Outputs2 = int(annotation.labels['DL_Outputs'][0])
        if "DL_SocialInnovation" in annotation.labels.keys():
            DL_SocialInnovation2 = int(annotation.labels['DL_SocialInnovation'][0])

    if DL_Actors2 == 0:
        frequency_0_ann2_Actors = frequency_0_ann2_Actors + 1
    if DL_Actors2 == 1:
        frequency_1_ann2_Actors = frequency_1_ann2_Actors + 1
    if DL_Actors2 == 2:
        frequency_2_ann2_Actors = frequency_2_ann2_Actors + 1
    if DL_Actors2 == 3:
        frequency_3_ann2_Actors = frequency_3_ann2_Actors + 1
    if DL_Innovativeness2 == 0:
        frequency_0_ann2_Innovativeness = frequency_0_ann2_Innovativeness + 1
    if DL_Innovativeness2 == 1:
        frequency_1_ann2_Innovativeness = frequency_1_ann2_Innovativeness + 1
    if DL_Innovativeness2 == 2:
        frequency_2_ann2_Innovativeness = frequency_2_ann2_Innovativeness + 1
    if DL_Innovativeness2 == 3:
        frequency_3_ann2_Innovativeness = frequency_3_ann2_Innovativeness + 1
    if DL_Objective2 == 0:
        frequency_0_ann2_Objectives = frequency_0_ann2_Objectives + 1
    if DL_Objective2 == 1:
        frequency_1_ann2_Objectives = frequency_1_ann2_Objectives + 1
    if DL_Objective2 == 2:
        frequency_2_ann2_Objectives = frequency_2_ann2_Objectives + 1
    if DL_Objective2 == 3:
        frequency_3_ann2_Objectives = frequency_3_ann2_Objectives + 1
    if DL_Outputs2 == 0:
        frequency_0_ann2_Outputs = frequency_0_ann2_Outputs + 1
    if DL_Outputs2 == 1:
        frequency_1_ann2_Outputs = frequency_1_ann2_Outputs + 1
    if DL_Outputs2 == 2:
        frequency_2_ann2_Outputs = frequency_2_ann2_Outputs + 1
    if DL_Outputs2 == 3:
        frequency_3_ann2_Outputs = frequency_3_ann2_Outputs + 1
    if DL_SocialInnovation2 == 0:
        frequency_0_ann2_SI = frequency_0_ann2_SI + 1
    if DL_SocialInnovation2 == 1:
        frequency_1_ann2_SI = frequency_1_ann2_SI + 1
    if DL_SocialInnovation2 == 2:
        frequency_2_ann2_SI = frequency_2_ann2_SI + 1
    if DL_SocialInnovation2 == 3:
        frequency_3_ann2_SI = frequency_3_ann2_SI + 1
csv_file.close()
print("Ann1,Actors = 0: "+str(frequency_0_ann1_Actors))
print("Ann1,Actors = 1: "+str(frequency_1_ann1_Actors))
print("Ann1,Actors = 2: "+str(frequency_2_ann1_Actors))
print("Ann1,Actors = 3: "+str(frequency_3_ann1_Actors))
print("Ann2,Actors = 0: "+str(frequency_0_ann2_Actors) )
print("Ann2,Actors = 1: "+str(frequency_1_ann2_Actors))
print("Ann2,Actors = 2: "+str(frequency_2_ann2_Actors))
print("Ann2,Actors = 3: "+str(frequency_3_ann2_Actors))

print("Ann1,Objectives = 0: "+str(frequency_0_ann1_Objectives))
print("Ann1,Objectives = 1: "+str(frequency_1_ann1_Objectives ))
print("Ann1,Objectives = 2: "+str(frequency_2_ann1_Objectives ))
print("Ann1,Objectives = 3: "+str(frequency_3_ann1_Objectives))

print("Ann2,Objectives = 0: "+str(frequency_0_ann2_Objectives))
print("Ann2,Objectives = 1: "+str(frequency_1_ann2_Objectives ))
print("Ann2,Objectives = 2: "+str(frequency_2_ann2_Objectives))
print("Ann2,Objectives = 3: "+str(frequency_3_ann2_Objectives))

print("Ann1,Outputs = 0: "+str(frequency_0_ann1_Outputs ))
print("Ann1,Outputs = 1: "+str(frequency_1_ann1_Outputs ))
print("Ann1,Outputs = 2: "+str(frequency_2_ann1_Outputs))
print("Ann1,Outputs = 3: "+str(frequency_3_ann1_Outputs))

print("Ann2,Outputs = 0: "+str(frequency_0_ann2_Outputs ))
print("Ann2,Outputs = 1: "+str(frequency_1_ann2_Outputs))
print("Ann2,Outputs = 2: "+str(frequency_2_ann2_Outputs))
print("Ann2,Outputs = 3: "+str(frequency_3_ann2_Outputs ))

print("Ann1,Innovativeness = 0: "+str(frequency_0_ann1_Innovativeness ))
print("Ann1,Innovativeness = 1: "+str(frequency_1_ann1_Innovativeness ))
print("Ann1,Innovativeness = 2: "+str(frequency_2_ann1_Innovativeness ))
print("Ann1,Innovativeness = 3: "+str(frequency_3_ann1_Innovativeness ))

print("Ann2,Innovativeness = 0: "+str(frequency_0_ann2_Innovativeness ))
print("Ann2,Innovativeness = 1: "+str(frequency_1_ann2_Innovativeness ))
print("Ann2,Innovativeness = 2: "+str(frequency_2_ann2_Innovativeness ))
print("Ann2,Innovativeness = 3: "+str(frequency_3_ann2_Innovativeness))

print("Ann1,SI = 0: "+str(frequency_0_ann1_SI ))
print("Ann1,SI = 1: "+str(frequency_1_ann1_SI ))
print("Ann1,SI = 2: "+str(frequency_2_ann1_SI ))
print("Ann1,SI = 3: "+str(frequency_3_ann1_SI))

print("Ann2,SI = 0: "+str(frequency_0_ann2_SI))
print("Ann2,SI = 1: "+str(frequency_1_ann2_SI))
print("Ann2,SI = 2: "+str(frequency_2_ann2_SI))
print("Ann2,SI = 3: "+str(frequency_3_ann2_SI))

print()
print('Exact match,Objectives: '+str(Objectives_exact_match))
print('Exact match,Actors: '+str(Actors_exact_match))
print('Exact match,Outputs: '+str(Outputs_exact_match))
print('Exact match,Innovativeness: '+str(Innovativeness_exact_match))
print('Exact match,SI: '+str(SI_exact_match))

print('1 diff,Objectives: '+str(Objectives_1diff))
print('1 diff,Actors: '+str(Actors_1diff))
print('1 diff,Outputs: '+str(Outputs_1diff))
print('1 diff,Innovativeness: '+str(Innovativeness_1diff))
print('1 diff,SI: '+str(SI_1diff))

print('2 diff,Objectives: '+str(Objectives_2diff))
print('2 diff,Actors: '+str(Actors_2diff))
print('2 diff,Outputs: '+str(Outputs_2diff))
print('2 diff,Innovativeness: '+str(Innovativeness_2diff))
print('2 diff,SI: '+str(SI_2diff))

print('3 diff,Objectives: '+str(Objectives_3diff))
print('3 diff,Actors: '+str(Actors_3diff))
print('3 diff,Outputs: '+str(Outputs_3diff))
print('3 diff,Innovativeness: '+str(Innovativeness_3diff))
print('3 diff,SI: '+str(SI_3diff))



