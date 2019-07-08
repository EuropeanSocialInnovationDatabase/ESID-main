import json
import os
from os.path import isfile, join
import nltk
from pandas import DataFrame

Orig_path = "Data/OrigData/"
Summ_path = "Data/Summaries/"

files = [f for f in os.listdir(Orig_path) if isfile(join(Orig_path, f))]
#file_out = file("Data/test.json","w")
jall = []
for file in files:
    orig_text = open(Orig_path+file,'r').read()
    sum_text = open(Summ_path + file, 'r').read()

    orig_sentences = nltk.sent_tokenize(orig_text.decode("utf-8"))
    sum_sentences = nltk.sent_tokenize(sum_text.decode("utf-8"))
    labels = []
    sentences = []
    sum_text = ""
    str_labels = ""
    for sent in orig_sentences:
        if sent in sum_sentences:
            labels.append(1)
            str_labels = str_labels + "1\n"
            sum_text = sum_text + " \n" + sent
        else:
            labels.append(0)
            str_labels = str_labels + "0\n"
        str_labels = str_labels[:-1]
        sentences.append(sent)
    df = DataFrame(labels)
    labels = "\n".join(str(labels))
    js = {"doc":orig_text,"summaries":sum_text,"extractive_summary":sum_text,"labels":str_labels}
    jall.append(js)

st = json.dumps(jall)
with open("Data/training_si_v2.json", 'w') as f:
    json.dump(jall,f)


