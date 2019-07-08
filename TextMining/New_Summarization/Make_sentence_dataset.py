from os import listdir
from random import randint

import numpy as np
import torch
from os.path import isdir, join, isfile
import nltk

from models import InferSent
model_version = 1
MODEL_PATH = "encoder/infersent%s.pkl" % model_version
params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                'pool_type': 'max', 'dpout_model': 0.0, 'version': model_version}
model = InferSent(params_model)
model.load_state_dict(torch.load(MODEL_PATH))
use_cuda = False
model = model.cuda() if use_cuda else model
W2V_PATH = '../Resources/glove.840B.300d.txt' if model_version == 1 else '../dataset/fastText/crawl-300d-2M.vec'
model.set_w2v_path(W2V_PATH)
model.build_vocab_k_words(K=2000000)

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

#cs = cosine(model.encode(['Obama is the president of the United States.'])[0], model.encode(['Obama is not a U.S. president.'])[0])
#print(cs)
summaries_folder = "Data/Summaries/"
orig_folder = "Data/OrigData/"
summaries = [f for f in listdir(summaries_folder) if isfile(join(summaries_folder, f))]
orig_data = [f for f in listdir(orig_folder) if isfile(join(orig_folder, f))]
sentences = open("sentences_dataset_summaries_new_datasets.txt","w")
for sum in summaries:
    for o in orig_data:
        if sum == o:
            sum_f = open(summaries_folder+sum,"r")
            summary_text = sum_f.read()
            orig_f = open(orig_folder + sum, "r")
            orig_text = orig_f.read()
            summary_sentences = nltk.sent_tokenize(summary_text)
            orig_sentences = nltk.sent_tokenize(orig_text)
            for sent in orig_sentences:
                sent = sent.replace('\n',' ').replace('\t',' ')
                Sent_Found = False
                for sum_sent in summary_sentences:
                    sum_sent = sum_sent.replace('\n',' ').replace('\t',' ')
                    if cosine(model.encode([sum_sent])[0],model.encode([sent])[0])>0.8:
                        sentences.write(sent+"\t1\n")
                        Sent_Found = True
                if Sent_Found==False:
                    sentences.write(sent+"\t0\n")
sentences.close()
