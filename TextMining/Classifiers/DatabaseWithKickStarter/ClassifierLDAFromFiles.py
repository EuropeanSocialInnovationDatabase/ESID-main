import os
from os.path import isfile, join

import gensim
import joblib
import pandas as pd
import pickle
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import shuffle
from gensim import corpora, models
from pprint import pprint
import sklearn as sklearn_lda
from sklearn.decomposition import LatentDirichletAllocation as LDA
import pyLDAvis
from pyLDAvis import sklearn as sklearn_lda
mypath = "Pos/"
onlyfiles = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
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
mypath = "Neg/"
onlyfiles = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
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
# Display new class counts
print(df_upsampled.classa.value_counts())
def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
df_upsampled = shuffle(df_upsampled).reset_index()

#processed_docs = df_upsampled['text'].map(preprocess)
#print(processed_docs[:10])

count_vectorizer = CountVectorizer(stop_words='english')

count_data = count_vectorizer.fit_transform(df_upsampled['text'])
# Create and fit the LDA model
number_topics = 50
number_words = 10
lda = LDA(n_components=number_topics)
lda.fit(count_data)

# Print the topics found by the LDA model
print("Topics found via LDA:")
def print_topics(model, count_vectorizer, n_top_words):
    words = count_vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(model.components_):
        print("\nTopic #%d:" % topic_idx)
        print(" ".join([words[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
print_topics(lda, count_vectorizer, number_words)

LDAvis_data_filepath = os.path.join('./ldavis_prepared_' + str(number_topics))
# # this is a bit time consuming - make the if statement True
# # if you want to execute visualization prep yourself
#if 1 == 1:
LDAvis_prepared = sklearn_lda.prepare(lda, count_data, count_vectorizer)

with open(LDAvis_data_filepath, 'wb') as f:
    pickle.dump(LDAvis_prepared, f)


print(LDAvis_prepared)

#LDAvis_prepared = np.real(LDAvis_prepared)

pyLDAvis.save_html(LDAvis_prepared, './ldavis_prepared_' + str(number_topics) + '.html')
