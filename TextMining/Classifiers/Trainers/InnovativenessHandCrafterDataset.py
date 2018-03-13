from os import listdir
from os.path import  join,isdir
import random
from sklearn import svm,tree
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from sklearn.feature_extraction import text as texta
from TextMining.Classifiers.Trainers.DatasetReader import read_dataset

def show_most_informative_features(vectorizer, clf, n=20):
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
    for (coef_1, fn_1), (coef_2, fn_2) in top:
        print "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2)

data_folder = "../../../Data/Innovativeness_created"

classes = [f for f in listdir(data_folder) if isdir(join(data_folder, f))]
innovative = []
other = []
dataset = []
for c in classes:
    folder = data_folder + "/" + c
    onlyfiles = [f for f in listdir(folder) if (f.endswith(".txt"))]
    for fi in onlyfiles:
        fil = open(folder+"/"+fi,"r")
        text = fil.read()
        if c == "Innovative":
            innovative.append(text)
            dataset.append([text,True])
        else:
            other.append(text)
            dataset.append([text,False])

random.shuffle(dataset)
i = 0
train = []
train_Y = []
test = []
test_Y = []
for d in dataset:
    if i<len(dataset)*0.8:
        train.append(d[0])
        train_Y.append(d[1])
    else:
        test.append(d[0])
        test_Y.append(d[1])
    i = i+1

print train_Y
stop_words1 = texta.ENGLISH_STOP_WORDS
count_vect = CountVectorizer(stop_words=stop_words1)
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

print "NaiveBayers"
clf = MultinomialNB().fit(X_train_tfidf, train_Y)

X_new_counts = count_vect.transform(test)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(X_new_tfidf)
print np.mean(predicted ==test_Y)
print(metrics.classification_report(test_Y, predicted))
print(metrics.confusion_matrix(test_Y,predicted,labels=[False,True]))
new_doc_array,new_text_array,objectives,actors,outputs,innovativeness = read_dataset()

X_new_counts2 = count_vect.transform(new_text_array)
X_new_tfidf2 = tfidf_transformer.transform(X_new_counts2)
predicted2 = clf.predict(X_new_tfidf2)
print np.mean(predicted2 ==innovativeness)
print(metrics.classification_report(innovativeness, predicted2))
print(metrics.confusion_matrix(innovativeness,predicted2,labels=[False,True]))
print show_most_informative_features(count_vect, clf, n=100)


