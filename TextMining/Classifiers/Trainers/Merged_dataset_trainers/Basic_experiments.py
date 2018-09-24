from os import listdir
from os.path import isfile, join
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.svm import SVC


def read_files(path):
    ann1files = [f for f in listdir(path) if isfile(join(path, f))]

    annotations = []

    for ann in ann1files:
        content = ""
        if ".txt" in ann:
            objective = -1
            actors = -1
            outputs = -1
            innovativeness = -1
            f = open(path +'/'+ann,'r')
            lines = f.readlines()
            for line in lines:
                content = content + line
            f = open(path + "/" + ann.replace('.txt','.ann'), "r")
            lines = f.readlines()
            for line in lines:
                if "Objectives:" in line:
                    objective = int(line.split(':')[1].replace('\r\n',''))
                if "Actors:" in line:
                    actors = int(line.split(':')[1].replace('\r\n',''))
                if "Outputs:" in line:
                    outputs = int(line.split(':')[1].replace('\r\n',''))
                if "Innovativenss:" in line:
                    innovativeness = int(line.split(':')[1].replace('\r\n',''))
                if "SI:" in line:
                    si = int(line.split(':')[1].replace('\r\n',''))
            annotations.append([ann,content,objective,actors,outputs,innovativeness,si])
    return annotations
class UniversalClassifier():
    def __init__(self):
        pass

    def train_RF_words_only(self,X_train,y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        print("Training")
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        # self.clf =SVC()
    def train_NB_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        print("Training")
        self.clf = MultinomialNB()
        self.clf.fit(X_train_tf, y_train)

    def train_SVM_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        print("Training")
        self.clf = SVC()
        self.clf.fit(X_train_tf, y_train)
        # self.clf.fit(features2, y)
        print("Trained")
    def predict_words_only(self,X_test):
        X_new_counts = self.count_vect1.transform(X_test)
        X_test_tf = self.tf_transformer.transform(X_new_counts)
        y_pred = self.clf.predict(X_test_tf)
        return y_pred
    def print_reports(self,y_pred,y_test):
        print(sklearn.metrics.classification_report(y_pred, y_test))
        print(sklearn.metrics.confusion_matrix(y_pred, y_test))


if  __name__ == '__main__':
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshops"
    #path = "../../../../Helpers/SI_dataset/Output/SI_only"
    annotations = read_files(path)
    texts = []
    objectives = []
    for anns in annotations:
        texts.append(anns[1])
        objectives.append(anns[5])
    df = pd.DataFrame({'text': texts, 'classa': objectives})
    print(df.classa.value_counts())
    folder = sklearn.model_selection.KFold(5)
    for  train_index, test_index in folder.split(df):
        X_train = df['text'][train_index]
        y_train = df['classa'][train_index]
        X_test = df['text'][test_index]
        y_test = df['classa'][test_index]
        cls = UniversalClassifier()
        cls.train_SVM_words_only(X_train,y_train)
        y_pred = cls.predict_words_only(X_test)
        cls.print_reports(y_pred, y_test)
