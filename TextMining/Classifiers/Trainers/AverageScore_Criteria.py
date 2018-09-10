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
for doc in r1.documents:
    print(doc)
    doc_count = 1.0
    DL_Actors1 = 0
    DL_Innovativeness1 = 0
    DL_Objective1 = 0
    DL_Outputs1 =0
    DL_SocialInnovation1 = 0
    DL_Actors2 = 0
    DL_Innovativeness2 = 0
    DL_Objective2 = 0
    DL_Outputs2 = 0
    DL_SocialInnovation2 = 0
    DL_Actors3 = 0
    DL_Innovativeness3 = 0
    DL_Objective3 = 0
    DL_Outputs3 = 0
    DL_SocialInnovation3 = 0
    document = r1.documents[doc]
    document_content = ''
    for annotation in document.annotations:
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
    for doc2 in r2.documents:
        if doc2 == doc:
            doc_count = 2.0
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
    for doc2 in cr.documents:
        if doc2 == doc:
            doc_count = 3.0
            document2 = cr.documents[doc2]
            for annotation in document2.annotations:
                if "DL_Actors" in annotation.labels.keys():
                    DL_Actors3 =int( annotation.labels['DL_Actors'][0])
                if "DL_Innovativeness" in annotation.labels.keys():
                    DL_Innovativeness3 = int(annotation.labels['DL_Innovativeness'][0])
                if "DL_Objective" in annotation.labels.keys():
                    DL_Objective3 = int(annotation.labels['DL_Objective'][0])
                if "DL_Outputs" in annotation.labels.keys():
                    DL_Outputs3 = int(annotation.labels['DL_Outputs'][0])
                if "DL_SocialInnovation" in annotation.labels.keys():
                    DL_SocialInnovation3 = int(annotation.labels['DL_SocialInnovation'][0])
    DL_Actors_total = (DL_Actors1 + DL_Actors2+DL_Actors3)/doc_count
    DL_Innovativeness_total = (DL_Innovativeness1+DL_Innovativeness2+DL_Innovativeness3)/doc_count
    DL_Objective_total = (DL_Objective1+DL_Objective2+DL_Objective3)/doc_count
    DL_Outputs_total = (DL_Outputs1+DL_Outputs2+DL_Outputs3)/doc_count
    DL_SocialInnovation_total = (DL_SocialInnovation1 + DL_SocialInnovation2 + DL_SocialInnovation3) / doc_count

    file = open(directory+doc,'w')
    file.write("DL_Actors: "+str(DL_Actors_total)+'\n')
    file.write("DL_Innovativeness: " + str(DL_Innovativeness_total)+"\n")
    file.write("DL_Objective: " + str(DL_Objective_total)+'\n')
    file.write("DL_Outputs: " + str(DL_Outputs_total)+'\n')
    file.write("DL_SocialInnovation: " + str(DL_SocialInnovation_total)+'\n')
    file.write('\n\n')
    file.write(document.text.encode('utf-8'))

    file.close()




