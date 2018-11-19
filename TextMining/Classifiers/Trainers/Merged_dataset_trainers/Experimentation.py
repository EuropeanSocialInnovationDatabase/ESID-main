import MySQLdb
from os import listdir
from os.path import isfile, join
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.svm import SVC
from sklearn.utils import resample
from database_access import *
import pickle
import os



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

def transfer_to_database(annotations):
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    for ann in annotations:
        project = ann[0].replace('p_','').replace('.txt','')
        project = unicode(project,'utf-8')
        project_id = 0
        if project.isnumeric():
            sql = "SELECT * FROM EDSI.Projects where idProjects="+project
            cursor.execute(sql)
            results = cursor.fetchall()
            for res in results:
                project_id = res[0]
        else:
            sql = "SELECT * FROM EDSI.Projects where ProjectWebpage like '%{0}%'".format(project)
            cursor.execute(sql)
            results = cursor.fetchall()
            for res in results:
                project_id = res[0]
        if project_id == 0:
            continue
        sql = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,Social_innovation_overall,SourceModel)" \
              "Values ({0},{1},{2},{3},{4},{5},'{6}')".format(ann[4],ann[2],ann[3],ann[5],project_id,ann[6],"ManualAnnotation")
        cursor.execute(sql)
        db.commit()
    db.close()

def load_database_description_dataset():
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "Select * FROM TypeOfSocialInnotation"
    cursor.execute(sql)
    results = cursor.fetchall()
    annotations = []
    for res in results:
        output = res[1]
        objectives = res[2]
        actors = res[3]
        innovativeness = res[4]
        si = res[6]
        project_id = res[5]
        new_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(project_id)
        cursor.execute(new_sql)
        results2 = cursor.fetchall()
        description = ""
        for res2 in results2:
            description = description + " " +res2[2]
        if len(description)<20:
            continue
        annotations.append([project_id,description,objectives,actors,output,innovativeness,si])
    return annotations

class UniversalClassifier():
    def __init__(self):
        self.confusion_matrix = confusion_matrix([0, 0],[0, 0])
        self.obj = ['aim','objective','goal','vision','strive']
        self.targets = ['poor','refugees','unpriviledged','black','gay','LGBT','trans','aging']
        self.inprove = ['inprove','improve','better','greater','quality','cutting edge']
        self.things = ['language','food','money','health','care','social','insurance','legal']
        self.new = ['new','novel']
        self.things2 = ['method','model','product','service','application','technology','practice']
        self.things3 = ['software','tool','framework','book']
        self.new_tech = ['machine learning','artificial intelligence','3d print','bitcoin','blockchain','cryptocurrency','nano']
        self.actor = ['organisation','university','users','ngo','firm','company','actors','people']

    def train_RF_words_only(self,X_train,y_train):
        self.count_vect1 = CountVectorizer(max_features=1000000,ngram_range=(1,3))
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        self.clf.fit(X_train_tf, y_train)
        # self.clf =SVC()
    def train_cost_sensitive_RF_words_only(self,X_train,y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = RandomForestClassifier(n_jobs=3, n_estimators=150,class_weight={0: 90, 1: 50})
        self.clf.fit(X_train_tf, y_train)

    def save_RF_words_only(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.count_vect1, open(path+"/count_vectorizer.pck", 'wb'))
        pickle.dump(self.tf_transformer, open(path + "/tf_transformer.pck", 'wb'))
        pickle.dump(self.clf, open(path + "/classifier.pck", 'wb'))

    def load_RF_words_only(self,path):
        self.count_vect1 = pickle.load(open(path+"/count_vectorizer.pck", 'rb'))
        self.tf_transformer = pickle.load(open(path + "/tf_transformer.pck", 'rb'))
        self.clf = pickle.load(open(path + "/classifier.pck", 'rb'))
        return self

    def train_RF_features_only(self,X_train,y_train):
        train_vector = []
        for x in X_train:
            xa = x.lower()
            has_obj = 0
            has_target = 0
            has_improve = 0
            has_things = 0
            has_new = 0
            has_things2 = 0
            has_things3 = 0
            has_new_tech = 0
            has_actor = 0
            for o in self.obj:
                if o in xa:
                    has_obj = 1
            for o in self.targets:
                if o in xa:
                    has_target =1
            for o in self.inprove:
                if o in xa:
                    has_improve = 1
            for o in self.things:
                if o in xa:
                    has_things = 1
            for o in self.new:
                if o in xa:
                    has_new = 1
            for o in self.things2:
                if o in xa:
                    has_things2 = 1
            for o in self.things3:
                if o in xa:
                    has_things3 = 1
            for o in self.new_tech:
                if o in xa:
                    has_new_tech =1
            for o in self.actor:
                if o in xa:
                    has_actor =1
            train_vector.append([has_obj,has_target,has_improve,has_things,has_things2,has_things3,has_new,has_new_tech,has_actor])
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        self.clf.fit(train_vector, y_train)




    def predict_features_only(self,X_test):
        train_vector = []
        for x in X_test:
            xa = x.lower()
            has_obj = 0
            has_target = 0
            has_improve = 0
            has_things = 0
            has_new = 0
            has_things2 = 0
            has_things3 = 0
            has_new_tech = 0
            for o in self.obj:
                if o in x:
                    has_obj = 1
            for o in self.targets:
                if o in xa:
                    has_target = 1
            for o in self.inprove:
                if o in xa:
                    has_improve = 1
            for o in self.things:
                if o in xa:
                    has_things = 1
            for o in self.new:
                if o in xa:
                    has_new = 1
            for o in self.things2:
                if o in xa:
                    has_things2 = 1
            for o in self.things3:
                if o in xa:
                    has_things3 = 1
            for o in self.new_tech:
                if o in xa:
                    has_new_tech = 1
            for o in self.actor:
                if o in xa:
                    has_actor =1
            train_vector.append([has_obj, has_target, has_improve, has_things, has_things2,has_things3, has_new, has_new_tech,has_actor])
        y_pred = self.clf.predict(train_vector)
        return y_pred


    def train_NB_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=100000000,ngram_range=(1,6))
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = MultinomialNB()
        self.clf.fit(X_train_tf, y_train)

    def train_SVM_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = SVC()
        self.clf.fit(X_train_tf, y_train)
        # self.clf.fit(features2, y)
        #print("Trained")
    def predict_words_only(self,X_test):
        X_new_counts = self.count_vect1.transform(X_test)
        X_test_tf = self.tf_transformer.transform(X_new_counts)
        y_pred = self.clf.predict(X_test_tf)
        return y_pred

    def print_reports(self,y_pred,y_test):
        print(sklearn.metrics.classification_report(y_pred, y_test))
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test)
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        print(new_confusion_matrix)
    def print_final_report(self):
        print("Overall confusion matrix:")
        print(self.confusion_matrix)
        overall_TP = 0.0
        overall_FP = 0.0
        overall_FN = 0.0
        precision = [0,0]
        recall = [0,0]
        F1score = [0,0]
        for i in range(0,len(precision)):
            true_pos = 0.0+self.confusion_matrix[i][i]
            false_pos = 0.0
            false_neg = 0.0
            for j in range(0,len(precision)):
                if j == i:
                    continue
                false_neg = false_neg + self.confusion_matrix[i][j]
            for j in range(0,len(precision)):
                if j == i:
                    continue
                false_pos = false_pos + self.confusion_matrix[j][i]
            overall_TP = overall_TP + true_pos
            overall_FP = overall_FP + false_pos
            overall_FN = overall_FN + false_neg
            if (true_pos+false_pos)!=0:
                precision[i] = true_pos/(true_pos+false_pos)
            if true_pos ==0 and (true_pos+false_pos)==0:
                precision[i] = 1.0
            if (true_pos + false_neg) != 0:
                recall[i] = true_pos/(true_pos+false_neg)
            if true_pos ==0 and (true_pos+false_neg)==0:
                recall[i] = 1.0
            if precision[i]+recall[i] >0:
                F1score[i] = 2*precision[i]*recall[i]/(precision[i]+recall[i])
            else:
                F1score[i] = 0.0
            print(str(i)+"\t\t"+str(round(precision[i],2))+"\t\t\t"+str(round(recall[i],2))+"\t\t"+str(round(F1score[i],2)))
        overall_precision = overall_TP/(overall_FP+overall_TP)
        overall_recall = overall_TP/(overall_TP+overall_FN)
        overall_F1score = 2*overall_precision*overall_recall/(overall_precision+overall_recall)
        print("Overall\t"+str(round(overall_precision,2))+"\t\t\t"+str(round(overall_recall,2))+"\t\t"+str(round(overall_F1score,2)))



if  __name__ == '__main__':
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded"
    #path = "../../../../Helpers/SI_dataset/Output/SI_withExcluded3"
    #path = "../../../../Helpers/SI_dataset/Output/SI_only"
    annotations = read_files(path)
    #annotations = load_database_description_dataset()
    #transfer_to_database(annotations)
    #exit(1)
    texts = []
    classA = []
    ### Working on Objectives
    print("Working on Objectives")

    for anns in annotations:
        texts.append(anns[1])
        value = anns[2]
        if value>=2:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    df_majority = df[df.classa == 1]
    df_minority = df[df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                      replace=True,     # sample with replacement
                                      n_samples=300,    # to match majority class
                                      random_state=83293) # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled],ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    df = df_upsampled

    cls = UniversalClassifier()
    i = 0


    folder = sklearn.model_selection.KFold(5)
    for train_index, test_index in folder.split(df):
        print("Fold "+str(i))
        i = i+1
        X_train = df['text'][train_index]
        y_train = df['classa'][train_index]
        X_test = df['text'][test_index]
        y_test = df['classa'][test_index]
        cls = UniversalClassifier()
        cls.train_RF_words_only(X_train, y_train)
        y_pred = cls.predict_words_only(X_test)
        cls.print_reports(y_pred, y_test)

    cls = UniversalClassifier()
    cls.train_RF_words_only(df['text'], df['classa'])
    cls.save_RF_words_only('Objectives_RF1')
    cls.load_RF_words_only('Objectives_RF1')
    prediction = cls.predict_words_only(["""Many voters would have forgiven David Cameron if he had failed to deliver on his campaign promise to hold an EU referendum, according to a study from the University of Exeter.

The research, funded by the Economic and Social Research Council, showed that 28% of people would have seen their view of the former prime minister significantly diminish if he hadn't held the vote.

This is compared with 70% who said his reputation would have been unchanged.

Dr Catarina Thomson, a member of the research team, said: Failed promises, backing down on threats or flip-flopping on policy positions are often assumed to lead to a loss in support.

"But in the case of David Cameron, going back on his campaign promises meant this loss could have been manageable.
Article share tools

""",
"""

The maximum bet on fixed-odds betting terminals will be cut from April after the government bowed to pressure.

Ministers had been facing a parliamentary defeat, with several Tory MPs joining opposition politicians to table amendments to the finance bill.

The chancellor said in the Budget the maximum bet would be reduced from 100 to 2 from October.

But that led to accusations of a delay - with sports minister Tracey Crouch resigning in protest.

Several former ministers - including Boris Johnson, Iain Duncan Smith and Justine Greening - tabled amendments designed to force the government to make the change from April.

Fixed-odds terminals were introduced in casinos and betting shops in 1999, and offer computerised games at the touch of a button.
What has the government done?

Culture Secretary Jeremy Wright said: "The government has listened and will now implement the reduction in April 2019."

Mr Wright added that a planned increase in Remote Gaming Duty, paid by online gaming firms, would be brought forward to April to cover the negative impact on the public finances.

Ms Crouch said she welcomed the decision and was pleased that "common sense" had prevailed.
""",


    """Active ageing applies to people of all ages so that they fulfil their maximum potential and enjoy the best possible quality of life. The increasing number of older people living with dementia is a recognised global health challenge that requires a range of innovative solutions if people affected by dementia, their families and their paid and unpaid carers are all to actively age. The built environment is one area of innovation that has the potential to provide a suitably stimulating, safe and comfortable place for people living with dementia to enjoy the final phase of their life. Western Home Communities (WHC) is a not-for-profit social care provider in the town of Cedar Falls (population c.40,000 people) in the mid-Western state of Iowa. WHC was founded in 1912 as the Western Old Peoples Home, a ministry of the Evangelical Association, and over the last 30 years has expanded and innovated to meet the needs of older people. In 1989 it opened one of Iowas first independent living communities and this was so successful that further similar developments followed in the early 1990s as older people, defined as being aged 55 years and over, wanted to live in such an age-friendly environment. Further relatively small scale independent and assisted living facilities followed enabling growth and an innovative partnership with AHTS Architects and Orfield Laboratories, a world leading research centre famous for having the quietest room in the world, to develop a small scale facility for people living with dementia. The result was The Cottages, two small nursing homes for 32 residents with dementia designed to develop perceptual and cognitive standards for the design of living environments. The residents decide how their daily life unfolds within the framework of a household model of care. The homes opened in June 2015 and provide people with living with dementia a state of the art living environment and a place where further refinements can be tested and developed. The work was acknowledged with the Dementia Design Innovation of the Year Award and the International Dementia Conference held in the UK in November 2016. In common with many social care providers, WHC provides opportunities for voluntary activity through their FRIENDS programme. F = Friendship R = Rewarding I = Inspiring E = Extending N = Network D = Delivering S = Satisfying In relation to the active ageing index, the new nursing home provide a safe and stimulating environment for people living with dementia. The environment is designed to enhance the mental well-being of residents through the living space and services that are provided. The Western Home Communities provides and relies on voluntary activities to provide additional services to residents that are likely to be beneficial to all concerned. """,
    """The impact of technology on societies continues to advance at a great pace with a wide range of effects. It can
    play a positive role in building social connections through making communication easier, it can enhance learning o
    pportunities and remotely monitor health indicators for a range of conditions. Many of these technological developments
    emerge from large corporations or public-private partnership projects but there has historically been scope for individual
    inventors or small groups of people to develop innovative ideas into practical solutions. There is still considerable scope for
    people to work together to develop new ideas using technology for socially beneficial purposes that can contribute to active ageing.
    Open Technology Laboratories (OTELO) started in the towns of Gmunden (population c.13,000) and Vocklabruck (population c. 12,000) in upper Austria in 2010 and are spaces that provide free to use basic infrastructure for people of all ages to work together on experimental ideas and projects. There is now a network of 16 OTELO spaces across Austria with the local municipality providing the space and basic infrastructure along with scope for leisure and recreational activities. The aim of OTELO is offer a combination of open access to a laboratory work space known as a node with the social aim of community building by complementing social and leisure activities with science and technology. The individual OTELOs are managed and operated by a volunteer committee who provide support for people and groups to develop ideas into viable projects, some of which can become marketable products or the basis for a business. Individuals and groups contribute modest fees towards the operation of the facility and provide additional resources that they need to develop and test their ideas. They are open to people of all ages and look to work in partnership with local schools and colleges, universities and businesses in developing new ideas, testing them and sharing knowledge and learning opportunities particularly with children and young people. For example, several OTELOs offer Kids Experience Technology programmes that enable school age children to learn about science and technology through inter-active experiences that are intended to be fun and inspiring. There is also scope for communal social activities such as community gardening, alternative local currencies that operate alongside people developing solar cookers and alternative forms of mobility. OTELOs also receive income from grants and donations in kind from the other corporate sector and other institutions to keep user costs low. In relation to active ageing, OTELOs offer the opportunity for voluntary activity in the operation and management of such institutions. It provides open access to lifelong learning opportunities in science and technology for people of all ages supplemented by leisure and recreational activities with a social purpose dimension to enhance community capacity through constructive and enjoyable interaction."""])
    print(prediction)