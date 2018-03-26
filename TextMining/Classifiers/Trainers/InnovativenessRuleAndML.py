import pickle
from os import listdir
import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

if __name__ == '__main__':
    print("Initializing")
    vect_innovativeness = pickle.load(open('../../Classifiers/Models/Vectorizer_Innovativeness.sav', 'rb'))
    voting_innovativeness = pickle.load(open('../../Classifiers/Models/Voting_innovtiveness.sav', 'rb'))
    data_folder = "../../Sample"
    onlyfiles = [f for f in listdir(data_folder) if (f.endswith(".txt"))]
    texts = []
    for f in onlyfiles:
        fa = open(data_folder + "/" + f, "r")
        txt = fa.read()
        texts.append(txt)

    count_vect = vect_innovativeness
    # stop_words=stop_words1
    X_train_counts = count_vect.transform(texts)
    print X_train_counts.shape
    print count_vect.vocabulary_.get(u'algorithm')
    tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)
    X_train_tf.shape
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    X_train_tfidf.shape
    objectives_pred = voting_innovativeness.predict(X_train_tfidf)
    print(objectives_pred)
    count_pos = 0
    count_all = 0

    i = 0
    for sample in texts:
        isInnovative = False
        if "innovation" in sample or "innovative" in sample or "novelty" in sample:
            isInnovative = True
        if (
                                "method" in sample or "product" in sample or "service" in sample or "application" in sample or "technology" in sample or "practice" in sample):

            list_items = ["method", "product", "service", "application", "technology", "practice"]
            index_list = []
            for item in list_items:
                indexes = [m.start() for m in re.finditer(item, sample)]
                index_list.extend(indexes)

            for index in index_list:
                end = len(sample)
                start = 0
                if index - 500 > 0:
                    start = index - 500
                if index + 500 < len(sample):
                    end = index + 500
                substr = sample[start:end]
                if (
                                        "new" in substr or "novel" in substr or "alternative" in substr or "improved" in substr or "cutting edge" in substr or "better" in substr):
                    isInnovative = True

        if isInnovative:
            objectives_pred[i] = True
        i = i+1
    for o in objectives_pred:
        count_all = count_all + 1
        if o == True:
            count_pos = count_pos + 1
    print "Voting on Innovativeness"
    print "All:" + str(count_all)
    print "Positive:" + str(count_pos)