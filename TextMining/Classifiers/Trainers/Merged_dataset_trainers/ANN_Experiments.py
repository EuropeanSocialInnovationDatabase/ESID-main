import MySQLdb
from os import listdir
from os.path import isfile, join
import pandas as pd
import sklearn
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dropout, Flatten, Dense, Activation, LSTM
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from database_access import *
from keras.models import model_from_json
from sklearn.model_selection import KFold
from keras import metrics
import numpy as np
import os
import pickle



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

class UniversalNNClassifier():
    def __init__(self):
        os.environ['PYTHONHASHSEED'] = '4'
        np.random.seed(523)
        self.max_words = 200000
        self.batch_size = 16
        self.epochs = 100
        self.GLOVE_DIR = "../../../../Helpers/BratDataProcessing/Glove_dir"
        self.MAX_SEQUENCE_LENGTH = 1100
        self.EMBEDDING_DIM = 200
        pass

    def train_CNN_words_only(self,X_train,y_train):
        embeddings_index = {}
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.tokenizer.fit_on_texts(X_train)
        sequences = self.tokenizer.texts_to_sequences(X_train)

        word_index = self.tokenizer.word_index
        f = open(os.path.join(self.GLOVE_DIR, 'glove.6B.200d.txt'))
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        print('Found %s word vectors.' % len(embeddings_index))
        embedding_matrix = np.zeros((len(word_index) + 1, self.EMBEDDING_DIM))
        for word, i in word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
        embedding_layer = Embedding(len(word_index) + 1,
                                    self.EMBEDDING_DIM,
                                    weights=[embedding_matrix],
                                    input_length=self.MAX_SEQUENCE_LENGTH,
                                    trainable=False)
        Total_TP = 0
        Total_FP = 0
        Total_FN = 0


        early_stopping = EarlyStopping(monitor='val_loss', patience=5)
        y_train = to_categorical(y_train)
        model = None
        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(2048, 5, activation='relu'))
        model.add(MaxPooling1D(20))
        model.add(Dropout(0.2))
        model.add(Conv1D(512, 5, activation='relu'))
        model.add(MaxPooling1D(10))
        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(20,activation='relu'))
        model.add(Dense(2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='nadam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit(data, y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=0,
                                validation_split=0.1,
                                callbacks=[early_stopping]
                                )
        self.clf = model

    def save_CNN_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.tokenizer, open(path + "/tokenizer.pck", 'wb'))
        model_json = self.clf.to_json()
        with open(path+"/model_actors.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.clf.save_weights(path+"/model_actors.h5")

    def load_CNN_model(self,path):
        json_file = open(path+"/model_actors.json", 'r')
        loaded_model_json = json_file.read()
        self.tokenizer = pickle.load(open(path + "/tokenizer.pck", 'rb'))
        json_file.close()
        self.clf = model_from_json(loaded_model_json)
        # load weights into new model
        self.clf.load_weights(path+"/model_actors.h5")
        return self


    def predict_CNN(self,X_test):
        sequences = self.tokenizer.texts_to_sequences(X_test)
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        y_pred = self.clf.predict(data)
        y_binary = []
        for y in y_pred:
            if y[0] < 0.5:
                y_binary.append(1)
            else:
                y_binary.append(0)
        return y_binary

    def print_reports(self,y_pred,y_test):
        print(sklearn.metrics.classification_report(y_pred, y_test))
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test)
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        print(new_confusion_matrix)



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

    cls = UniversalNNClassifier()
    i = 0

    folder = KFold(5)
    for train_index, test_index in folder.split(df):
        print("Fold "+str(i))
        i = i+1
        X_train = df['text'][train_index]
        y_train = df['classa'][train_index]
        X_test = df['text'][test_index]
        y_test = df['classa'][test_index]
        cls = UniversalNNClassifier()
        cls.train_CNN_words_only(X_train, y_train)
        y_pred = cls.predict_CNN(X_test)
        cls.print_reports(y_pred, y_test)

    cls = UniversalNNClassifier()
    cls.train_CNN_words_only(df['text'], df['classa'])
    cls.save_CNN_model("Objectives_CNN")
    prediction = cls.predict_CNN(["""Many voters would have forgiven David Cameron if he had failed to deliver on his campaign promise to hold an EU referendum, according to a study from the University of Exeter.

    The research, funded by the Economic and Social Research Council, showed that 28% of people would have seen their view of the former prime minister significantly diminish if he hadn't held the vote.

    This is compared with 70% who said his reputation would have been unchanged.

    Dr Catarina Thomson, a member of the research team, said: Failed promises, backing down on threats or flip-flopping on policy positions are often assumed to lead to a loss in support.

    "But in the case of David Cameron, going back on his campaign promises meant this loss could have been manageable.
    Article share tools

    """, """More than 40,000 women in England have not received information regarding cervical cancer screening after a failure to send out letters by the NHS.

    The errors were made between January and June.

    Around 4,000 of them were results of tests, the remainder were letters inviting them for screening or reminding them they were due.

    Between 150 and 200 of the test results that were not sent out were abnormal results.

    Nearly half of these have since been chased up and no harm has been caused, an NHS England source said.

        Millions of women miss out on smear tests

    It is thought many of these women had already got back in touch with their GP and gone for further testing after acting themselves when they did not get the result, or the abnormal results were subsequently found not to be concerning.

    The remainder are being contacted, the source said, with the risk of harm considered to be low.
    """,
                                         """Improving educational attainment across society is likely to have positive economic and social effects and the quest for knowledge and putting it to purposeful use is an important  part of the challenges that face European societies. In the last decade there has been a rapid growth of Massive Open Online Courses (MOOCs) predominantly from American universities in partnership with a number of foundations and private corporations that have enhanced the dominant position of English as the international language of academic life. However, there are many people who do not speak English and there is a large French speaking population around the world who can benefit from access to short courses of higher education. In response to the rise of MOOCs that use English, the French Ministry of National Education, Higher Education and Research committed an initial 20 million to a national digital education strategy that included the development of France Universite Numerique (FUN). It is a partnership of INRIA (a public sector institute for digital research), CINES (a public sector institute for ICT) and RENATER (a public interest group for telecommunications infrastructure) that is the national platform presented via a web portal. It also serves as an international portal for the Francophone world as MOOCs have been pioneered on a large scale in the English speaking world. FUN was launched in October 2013 and now has more than 750,000 registered users who have participated more than a million times in courses that now number nearly 200 from more than 60 partner institutions. The short courses cover a broad range of subjects and are all in French with some also offered in English to cater for the Anglophone world. FUN is part of a wider movement to promote a French-language international academic community and there is a broad mixture of users with the majority (61%) in the 25-50 age range, 13% are retired, 11% unemployed people and 9% are students showing the broad appeal of MOOCs. To register and take courses is free for users with modest fees for certification of completion and achievement. There are also plans for the development of MOOCs for vocational training to complement the academic and technical short courses that are currently on offer. As with all MOOC providers, the emphasis is on students interacting and learning from the presented sessions and from each other as well as completing the tasks that are required as part of the course. In relation to active ageing, FUN offers the MOOC experience to the French speaking population and should contribute to increasing educational attainment over the life course. It is interesting to note that it is used by a wide range of people showing that there is an enthusiasm for gaining knowledge for people of all ages. It is relevant to the active ageing indexs domain for the use of ICT and provides a powerful example of how learning is being transformed through the use of technology. While there are always risks of social innovations that rely on the use of ICT deepening the digital divide, the potential of MOOCs such as FUN to contribute to increasing educational attainment across the life course is very promising. There is a link between the level of educational attainment and employability over the life course so it is plausible that FUN can contribute to extending working lives as people learn new skills over their life course. """,
                                         """The impact of technology on societies continues to advance at a great pace with a wide range of effects. It can
                                         play a positive role in building social connections through making communication easier, it can enhance learning o
                                         pportunities and remotely monitor health indicators for a range of conditions. Many of these technological developments
                                         emerge from large corporations or public-private partnership projects but there has historically been scope for individual
                                         inventors or small groups of people to develop innovative ideas into practical solutions. There is still considerable scope for
                                         people to work together to develop new ideas using technology for socially beneficial purposes that can contribute to active ageing.
                                         Open Technology Laboratories (OTELO) started in the towns of Gmunden (population c.13,000) and Vocklabruck (population c. 12,000) in upper Austria in 2010 and are spaces that provide free to use basic infrastructure for people of all ages to work together on experimental ideas and projects. There is now a network of 16 OTELO spaces across Austria with the local municipality providing the space and basic infrastructure along with scope for leisure and recreational activities. The aim of OTELO is offer a combination of open access to a laboratory work space known as a node with the social aim of community building by complementing social and leisure activities with science and technology. The individual OTELOs are managed and operated by a volunteer committee who provide support for people and groups to develop ideas into viable projects, some of which can become marketable products or the basis for a business. Individuals and groups contribute modest fees towards the operation of the facility and provide additional resources that they need to develop and test their ideas. They are open to people of all ages and look to work in partnership with local schools and colleges, universities and businesses in developing new ideas, testing them and sharing knowledge and learning opportunities particularly with children and young people. For example, several OTELOs offer Kids Experience Technology programmes that enable school age children to learn about science and technology through inter-active experiences that are intended to be fun and inspiring. There is also scope for communal social activities such as community gardening, alternative local currencies that operate alongside people developing solar cookers and alternative forms of mobility. OTELOs also receive income from grants and donations in kind from the other corporate sector and other institutions to keep user costs low. In relation to active ageing, OTELOs offer the opportunity for voluntary activity in the operation and management of such institutions. It provides open access to lifelong learning opportunities in science and technology for people of all ages supplemented by leisure and recreational activities with a social purpose dimension to enhance community capacity through constructive and enjoyable interaction."""])
    print(prediction)
