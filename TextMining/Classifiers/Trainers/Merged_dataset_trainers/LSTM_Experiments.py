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
from sklearn.utils import resample

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

class LSTMClassifier():
    def __init__(self):
        os.environ['PYTHONHASHSEED'] = '4'
        np.random.seed(523)
        self.max_words = 10000
        self.batch_size = 16
        self.epochs = 100
        self.GLOVE_DIR = "../../../../Helpers/BratDataProcessing/Glove_dir"
        self.MAX_SEQUENCE_LENGTH = 1100
        self.EMBEDDING_DIM = 200
        pass

    def train_LSTM_words_only(self,X_train,y_train):
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

        early_stopping = EarlyStopping(monitor='val_loss', patience=5)
        y_train = to_categorical(y_train)
        model = None
        model = Sequential()
        model.add(embedding_layer)
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=512, kernel_size=2, padding='same', activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Dropout(0.2))
        model.add(LSTM(100))
        model.add(Dropout(0.2))
        model.add(Dense(2))
        model.add(Dropout(0.2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit(data, y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=0,
                                validation_split=0.1,
                                callbacks=[early_stopping]
                                )
        self.clf = model

    def save_LSTM_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.tokenizer, open(path + "/tokenizer.pck", 'wb'))
        model_json = self.clf.to_json()
        with open(path+"/model_actors.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.clf.save_weights(path+"/model_actors.h5")

    def load_LSTM_model(self,path):
        json_file = open(path+"/model_actors.json", 'r')
        loaded_model_json = json_file.read()
        self.tokenizer = pickle.load(open(path + "/tokenizer.pck", 'rb'))
        json_file.close()
        self.clf = model_from_json(loaded_model_json)
        # load weights into new model
        self.clf.load_weights(path+"/model_actors.h5")
        return self


    def predict_LSTM(self,X_test):
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
    np.random.seed(2)

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
        value = anns[5]
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
                                     replace=True,  # sample with replacement
                                     n_samples=500,  # to match majority class
                                     random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    df = df_upsampled

    # cls = LSTMClassifier()
    # i = 0
    #
    # folder = KFold(5)
    # for train_index, test_index in folder.split(df):
    #     print("Fold "+str(i))
    #     i = i+1
    #     X_train = df['text'][train_index]
    #     y_train = df['classa'][train_index]
    #     X_test = df['text'][test_index]
    #     y_test = df['classa'][test_index]
    #     cls = LSTMClassifier()
    #     cls.train_LSTM_words_only(X_train, y_train)
    #     y_pred = cls.predict_LSTM(X_test)
    #     cls.print_reports(y_pred, y_test)

    cls = LSTMClassifier()
    cls.train_LSTM_words_only(df['text'], df['classa'])
    cls.save_LSTM_model("Innovativeness_LSTM")
    #cls.load_LSTM_model("Objectives_LSTM")
    prediction = cls.predict_LSTM(["""A man accused of shooting dead his heavily pregnant ex-wife with a crossbow may face trial next year.

Sana Muhammad 35, died on Monday after the attack in Ilford, east London. Her son was delivered safely.

Ramanodge Unmathallegadoo, 50, formerly of Applegarth Drive, Ilford, has been charged with her murder.

During a hearing at the Old Bailey, the defendant, who has yet to enter a plea, was told a provisional trial date of 8 April 2019 had been set.

A plea hearing on 6 February was also scheduled.

Appearing via videolink, Mr Unmathallegadoo spoke only to confirm his name, age and British nationality when he appeared in court.

Mrs Muhammad, formerly known as Devi Unmathallegadoo, was eight months pregnant when she was attacked at her home in Applegarth Drive.

She was taken to hospital with an abdominal wound and pronounced dead at 11:00 GMT, less than four hours after the attack.

Her son was delivered by Caesarean section and "remains in a stable condition in a critical care unit", police said.

A trial would last two weeks, Judge Nicholas Hilliard QC told the court.

""",
                                   """Many voters would have forgiven David Cameron if he had failed to deliver on his campaign promise to hold an EU referendum, according to a study from the University of Exeter.

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


    """Meeting the challenges of an ageing society will require social change and innovation on a variety of levels ranging from 
    individuals and families through neighbourhoods and municipalities to national government and the operation of multi-national 
    corporations. The World Health Organisations Age Friendly World initiative highlights and supports municipalities around the world 
    to adapt to the challenges of ageing and the Finnish city of Tampere is part of this global network and movement. Tampere is the 
    largest inland city in any Nordic country with a population of over 220,000 in the municipality and over 360,000 people in the greater 
    metropolitan area. Tampere has adopted a mayoral system and with the Tampere Senior initiative has a strategic programme covering 
    the 2012-20 period. The main aims are to develop innovative solutions to better meet the needs of the increasing number of older 
    people through enabling them to feel safe, live independent in their own homes and changing social attitudes about older people and 
    ageing. An important element of the strategy is to involve people of all ages, especially older people who have an elder council as 
    a link to the municipality, in strengthening civil society and developing solutions as well as taking decisions. The initiative is a 
    partnership between the municipality, universities, companies and third sector organisations and an important outcome is the 
    development of evidence on active ageing in one virtual place. Enabling older people now to live independently has involved the 
    development of a new model of social care. The Kotitori (Home Market) system has the municipality as the major purchaser of social 
    care services reaching a service level agreement and annual contract with the Kotikori which acts as a social care service integrator 
    that manages and develops a network of service providers from the municipality, private and third sector providers. The Kotikori 
    provides information on housing, home care service, mobility, financial benefits, sports and leisure activities. Older people and 
    their families can then select the mix of care providers that meet their needs within an agreed budget from the municipality that 
    can be supplemented in the Home Market if they wish. The system appears to offer easier access to social care services, better control 
    of costs with improved productivity and higher satisfaction in care quality due to increased competition within a managed and 
    regulated framework. There is less work for the city with lower transaction costs and more privately funded services thus building 
    a better mixed economy of social care provision. In relation to active ageing, the social innovations in Tampere are relevant to 
    political participation through the elder council and the emphasis on involvement and participation that runs through the initiative. 
    The Kotikori reform of social care appears to offer improved access to health and social care services and the whole approach to 
    active and healthy ageing is to enable independent living for older people. """,

    """The impact of technology on societies continues to advance at a great pace with a wide range of effects. It can
    play a positive role in building social connections through making communication easier, it can enhance learning o
    pportunities and remotely monitor health indicators for a range of conditions. Many of these technological developments
    emerge from large corporations or public-private partnership projects but there has historically been scope for individual
    inventors or small groups of people to develop innovative ideas into practical solutions. There is still considerable scope for
    people to work together to develop new ideas using technology for socially beneficial purposes that can contribute to active ageing.
    Open Technology Laboratories (OTELO) started in the towns of Gmunden (population c.13,000) and Vocklabruck (population c. 12,000) in upper Austria in 2010 and are spaces that provide free to use basic infrastructure for people of all ages to work together on experimental ideas and projects. There is now a network of 16 OTELO spaces across Austria with the local municipality providing the space and basic infrastructure along with scope for leisure and recreational activities. The aim of OTELO is offer a combination of open access to a laboratory work space known as a node with the social aim of community building by complementing social and leisure activities with science and technology. The individual OTELOs are managed and operated by a volunteer committee who provide support for people and groups to develop ideas into viable projects, some of which can become marketable products or the basis for a business. Individuals and groups contribute modest fees towards the operation of the facility and provide additional resources that they need to develop and test their ideas. They are open to people of all ages and look to work in partnership with local schools and colleges, universities and businesses in developing new ideas, testing them and sharing knowledge and learning opportunities particularly with children and young people. For example, several OTELOs offer Kids Experience Technology programmes that enable school age children to learn about science and technology through inter-active experiences that are intended to be fun and inspiring. There is also scope for communal social activities such as community gardening, alternative local currencies that operate alongside people developing solar cookers and alternative forms of mobility. OTELOs also receive income from grants and donations in kind from the other corporate sector and other institutions to keep user costs low. In relation to active ageing, OTELOs offer the opportunity for voluntary activity in the operation and management of such institutions. It provides open access to lifelong learning opportunities in science and technology for people of all ages supplemented by leisure and recreational activities with a social purpose dimension to enhance community capacity through constructive and enjoyable interaction."""])
    print(prediction)
