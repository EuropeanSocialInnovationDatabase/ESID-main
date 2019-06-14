from os import listdir
from os.path import isfile, join
import nltk
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.utils import resample
from sklearn.metrics import classification_report

mypath = "Data"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and ".txt" in f]
sentences = []
for file in onlyfiles:
    print(file)
    text = open(mypath+"/"+file).read().decode('utf-8').strip()
    annotations = open(mypath+"/"+file.replace(".txt",".ann")).readlines()
    proc_annotations = []
    for ann in annotations:
        if "AnnotatorNotes" in ann:
            continue
        anns = ann.split("\t")
        if len(anns)==1:
            continue
        T = anns[0]
        if "A" in T:
            continue
        #print(T)
        #print(anns[2])
        sent = anns[2]
        temp = anns[1].split(" ")
        clas = temp[0]
        span_start = int(temp[1])
        if ";" in temp[2]:
            ta = temp[2].split(";")[0]
            temp[2] = ta
        span_end = int(temp[2])
        proc_annotations.append((T,clas,span_start,span_end,sent))
    sents = nltk.sent_tokenize(text)
    for s in sents:
        start = text.index(s)
        end = start + len(s)
        found = False
        for pa in proc_annotations:
            if pa[2]>=start and pa[3]<=end:
                sentences.append((s,pa[1]))
                found = True
        if found == False:
            sentences.append((s,"Neg"))
actor_cnt = 0
objectiv_cnt = 0
output_cnt = 0
innovativeness_cnt = 0
other = 0
objective_sents = []
other_sents = []
sentences = set(sentences)
for s in sentences:
    if s[1]=="SL_Actors_2":
        actor_cnt = actor_cnt + 1
    elif s[1]=="SL_Objective_1":
        objectiv_cnt = objectiv_cnt + 1
        objective_sents.append(s)
    elif s[1] == "SL_Outputs_3":
        output_cnt = output_cnt + 1
    elif s[1] == "SL_Innovativeness_4":
        innovativeness_cnt = innovativeness_cnt + 1
    else:
        other = other + 1
        other_sents.append(s)
    #print(s)
print("Objective sent: "+str(objectiv_cnt))
print("Actor sent: "+str(actor_cnt))
print("Output sent:"+str(output_cnt))
print("Innovativeness sent:"+str(innovativeness_cnt))
print("No class: "+str(other))
objective_sents = set(objective_sents)
print(objective_sents)
print(len(objective_sents))
other_sents = set(other_sents)
print(len(other_sents))

new_texts = []
new_labels =[]
counter = 20
for s in sentences:
    if s[1]=="SL_Objective_1":
        new_texts.append(s[0])
        new_labels.append(1)
    else:
        counter = counter-1
        if counter ==0:
            new_texts.append(s[0])
            new_labels.append(0)
            counter = 20





train = new_texts[0:int(0.8*len(new_texts))]
train_Y = new_labels[0:int(0.8*len(new_labels))]

test_s = new_texts[int(0.8*len(new_texts)):]
test_Y = new_labels[int(0.8*len(new_labels)):]
count_vect = CountVectorizer()
#stop_words=stop_words1
X_train_counts = count_vect.fit_transform(train)
print X_train_counts.shape
print count_vect.vocabulary_.get(u'algorithm')
tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
X_train_tf.shape
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
X_train_tfidf.shape

print "NaiveBayes"
clf = MultinomialNB().fit(X_train_tfidf, train_Y)

X_new_counts = count_vect.transform(test_s)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(X_new_tfidf)
print np.mean(predicted ==test_Y)
print(classification_report(test_Y, predicted))

print "RandomForest"
clf = RandomForestClassifier(n_estimators=200).fit(X_train_tfidf, train_Y)

X_new_counts = count_vect.transform(test_s)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(X_new_tfidf)
# for doc, category in zip(test, predicted):
#     print('%r => %s' % (doc, test_Y.target_names[category]))
#show_most_informative_features(count_vect,clf,100)
print np.mean(predicted ==test_Y)
print(classification_report(test_Y, predicted))

# for i in range(0,len(predicted)):
#     print(test_s[i])




