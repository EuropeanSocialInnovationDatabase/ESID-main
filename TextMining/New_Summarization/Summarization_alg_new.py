import pickle

import pandas as pd
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.utils import resample

f = open("sentences_dataset_summaries1.txt",'r')
lines = f.readlines()
data = []
for l in lines:
    dp = l.split('\t')
    tx = ""
    for d in range(0,len(dp)-1):
        tx = tx+" "+dp[d]
    data.append((dp[0],int(dp[-1].replace('\n',''))))
texts = []
labels = []
for d in data:
    texts.append(d[0])
    labels.append(d[1])
d = {'texts':texts,'labels':labels}
df = pd.DataFrame(data=d)
print(df.columns)

f_majority = df[df['labels']==0]
df_minority = df[df['labels']==1]
f_majority_upsampled = resample(f_majority,
                                 replace=True,     # sample with replacement
                                 n_samples=29850,    # to match majority class
                                 random_state=83293) # reproducible results
df_upsampled = pd.concat([df_minority, f_majority_upsampled])
df = df_upsampled.sample(frac=1).reset_index(drop=True)
print(df.groupby('labels').count())
texts2 = df['texts'].values
labels2 = df['labels'].values
train = texts2[0:int(0.8*len(texts2))]
trainY = labels2[0:int(0.8*len(labels2))]
test = texts2[int(0.8*len(texts2)):]
testY = labels2[int(0.8*len(labels2)):]

text_clf = Pipeline([('vect', CountVectorizer()),
                      ('tfidf', TfidfTransformer()),
                      ('clf', RandomForestClassifier()),
 ])

text_clf.fit(train,trainY)
pickle.dump(text_clf, open("RandomForestModel.pl", 'wb'))

predictions = text_clf.predict(test)

print(classification_report(testY,predictions))

#scores = cross_val_score(text_clf, df['texts'], df['labels'], cv=10,scoring='f1')
# final = 0
# # for score in scores:
# #     final = final + score
# # print scores
# print "Final:" + str(final/10)
