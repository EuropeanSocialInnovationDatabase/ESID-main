import json
import os

from os.path import isfile, join

import numpy as np
from rouge import Rouge
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.feature_extraction.text import CountVectorizer
import sklearn
from pyLDAvis import sklearn as sklearn_lda
import pickle
import pyLDAvis
import nltk
import statistics
import sys
# dirName = "Data/RandForest_GeneratedSummaries/"
# # Create target Directory if don't exist
# if not os.path.exists(dirName):
#     os.mkdir(dirName)
# path = "Data/TestDataOrig/"
# files = [f for f in os.listdir(path) if isfile(join(path, f))]
# with open("RandomForestSummarizer.pl", 'rb') as pickle_file:
#     classifier = pickle.load(pickle_file)
# for file in files:
#     summary = ""
#     text = open(path+file,"r").read()
#     sentences = nltk.sent_tokenize(text)
#     for sent in sentences:
#         prediction = classifier.predict([sent])
#         if prediction[0] == 1:
#             summary = summary + " " + sent
#
#     out = open(dirName+file,"w")
#     out.write(summary)
#     out.close()
# exit(5)

SumDirName = "Data/RandForest_GeneratedSummaries/"
OrugName = "Data/TestDataOrig/"

files = [f for f in os.listdir(OrugName) if isfile(join(OrugName, f))]
count_empty = 0
rouge1_pre = 0
rouge1_rec = 0
rouge1_f1 = 0
rouge2_pre = 0
rouge2_rec = 0
rouge2_f1 = 0
rougeL_pre = 0
rougeL_rec = 0
rougeL_f1 = 0
print(sys.getrecursionlimit())
sys.setrecursionlimit(10000 * 2080 + 10)

rouge = Rouge()
count_summaries = 0
hypothesis = []
reference = []
for file in files:
    sum = []
    origa = []
    orig = open(OrugName+file,"r").read()
    summ = open(SumDirName+file,"r").read()

    if summ == "":
        count_empty = count_empty + 1
    else:
        hypothesis.append(summ)
        reference.append(orig)
        sum.append(summ)
        origa.append(orig)
        scores = rouge.get_scores(sum, origa)
        rouge1_pre = rouge1_pre + scores[0]['rouge-1']['p']
        rouge1_rec = rouge1_rec + scores[0]['rouge-1']['r']
        rouge1_f1 = rouge1_f1 + scores[0]['rouge-1']['f']
        rouge2_pre = rouge2_pre + scores[0]['rouge-2']['p']
        rouge2_rec = rouge2_rec + scores[0]['rouge-2']['r']
        rouge2_f1 = rouge2_f1 + scores[0]['rouge-2']['f']
        rougeL_pre = rougeL_pre + scores[0]['rouge-l']['p']
        rougeL_rec = rougeL_rec + scores[0]['rouge-l']['r']
        rougeL_f1 = rougeL_f1 + scores[0]['rouge-l']['f']
        count_summaries = count_summaries + 1

#print("Projects with no summary:"+str(count_empty))
# Helper function
def print_topics(model, count_vectorizer, n_top_words):
    words = count_vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(model.components_):
        print("\nTopic #%d:" % topic_idx)
        print(" ".join([words[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))




rouge1_pre = rouge1_pre/count_summaries
rouge1_rec = rouge1_rec/count_summaries
rouge1_f1 = rouge1_f1/count_summaries
rouge2_pre = rouge2_pre/count_summaries
rouge2_rec = rouge2_rec/count_summaries
rouge2_f1 = rouge2_f1/count_summaries
rougeL_pre = rougeL_pre/count_summaries
rougeL_rec = rougeL_rec/count_summaries
rougeL_f1 = rougeL_f1/count_summaries
print("Rouge 1 p:"+str(rouge1_pre))
print("Rouge 1 r:"+str(rouge1_rec))
print("Rouge 1 f1:"+str(rouge1_f1))
print("Rouge 2 p:"+str(rouge2_pre))
print("Rouge 2 r:"+str(rouge2_rec))
print("Rouge 2 f1:"+str(rouge2_f1))
print("Rouge L p:"+str(rougeL_pre))
print("Rouge L r:"+str(rougeL_rec))
print("Rouge L f1:"+str(rougeL_f1))


# Tweak the two parameters below
number_topics = 20
number_words = 20

count_vectorizer = CountVectorizer(stop_words='english')

count_data = count_vectorizer.fit_transform(reference)
# Create and fit the LDA model
lda = LDA(n_components=number_topics)
lda.fit(count_data)

# Print the topics found by the LDA model
print("Topics found via LDA:")
print_topics(lda, count_vectorizer, number_words)

LDAvis_data_filepath = os.path.join('./ldavis_prepared_' + str(number_topics))
# # this is a bit time consuming - make the if statement True
# # if you want to execute visualization prep yourself
#if 1 == 1:
LDAvis_prepared = sklearn_lda.prepare(lda, count_data, count_vectorizer)

with open(LDAvis_data_filepath, 'wb') as f:
    pickle.dump(LDAvis_prepared, f)

# load the pre-prepared pyLDAvis data from disk
# with open(LDAvis_data_filepath,'rb') as f:
#     LDAvis_prepared = pickle.load(f)


list_sims = []
for i in range(0,len(hypothesis)):
    sum = hypothesis[i]
    text = reference[i]
    count_data = count_vectorizer.transform([sum])
    topics_sum = lda.transform(count_data)[0]
    summary_topics = []
    for i in range(0,20):
        if topics_sum[i]>0.0005:
            summary_topics.append(i)
    count_data = count_vectorizer.transform([text])
    topics_text = lda.transform(count_data)[0]
    text_topics = []
    for i in range(0,20):
        if topics_text[i]>0.0005:
            text_topics.append(i)
    topic_union = set(text_topics).union(set(summary_topics))
    topic_intersection = set(text_topics).intersection(set(summary_topics))
    list_sims.append(len(topic_intersection)/len(topic_union))
print(list_sims)
print(statistics.mean(list_sims))





print(LDAvis_prepared)

#LDAvis_prepared = np.real(LDAvis_prepared)

pyLDAvis.save_html(LDAvis_prepared, './ldavis_prepared_' + str(number_topics) + '.html')
