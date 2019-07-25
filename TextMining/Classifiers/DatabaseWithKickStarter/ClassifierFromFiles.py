from os import listdir
from os.path import isfile, join

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import shuffle

mypath = "PosIno/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
analyzer = CountVectorizer().build_analyzer()
stemmer = EnglishStemmer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))
dataset_text = []
dataset_labels = []
for file in onlyfiles:
    f = open(mypath + file,"r")
    text = f.read()
    classa = 1
    dataset_text.append(text)
    dataset_labels.append(classa)
mypath = "NegIno/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for file in onlyfiles:
    f = open(mypath + file,"r")
    text = f.read()
    classa = 0
    dataset_text.append(text)
    dataset_labels.append(classa)
df = pd.DataFrame({'text':dataset_text,'classa':dataset_labels})

# df_majority = df[df.classa==1]
# df_minority = df[df.classa==0]
# df_minority_upsampled = resample(df_minority,
#                                  replace=True,     # sample with replacement
#                                  n_samples=300,    # to match majority class
#                                  random_state=83293) # reproducible results
df_upsampled = df
# print df_upsampled
# exit()
print "New dataset"
# Display new class counts
print df_upsampled.classa.value_counts()

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()
#print df_upsampled

# train = text_array[0:int(0.8*len(text_array))]
# train_Y = innovativeness[0:int(0.8*len(actors))]
#
# test = text_array[int(0.8*len(text_array)):]
# test_Y = innovativeness[int(0.8*len(actors)):]

#categories = ['non actor', 'actor']
stopWords = set(stopwords.words('english'))
text_clf = Pipeline([('vect', CountVectorizer(analyzer=stemmed_words,stop_words=stopWords,ngram_range=(1,3))),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
 ])

scores = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='f1')
final = 0
for score in scores:
    final = final + score
print scores
print "F1 Final:" + str(final/10)


scores1 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='precision')
final = 0
print "Precision"
for score in scores1:
    final = final + score
print scores1
print "Precision Final:" + str(final/10)

scores2 = cross_val_score(text_clf, df_upsampled.text, df_upsampled.classa, cv=10,scoring='recall')
final = 0
print "Recall"
for score in scores2:
    final = final + score
print scores2
print "Recall Final:" + str(final/10)