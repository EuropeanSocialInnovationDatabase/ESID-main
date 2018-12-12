import MySQLdb
from os import listdir
from os.path import isfile, join
import pandas as pd
import sklearn
from keras import Sequential, Input
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dropout, Flatten, Dense, Activation, LSTM, Bidirectional, \
    Concatenate
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from database_access import *
from keras.models import model_from_json
from sklearn.model_selection import KFold
from keras import metrics
import numpy as np
import os
import pickle



def populate_ontology():
    ontology = {}
    ontology['bioeconomy'] = 0
    ontology['agriculture'] = 0
    ontology['bio_fuels'] = 0
    ontology['biomass'] = 0
    ontology['food_production'] = 0
    ontology['landscape_management'] = 0
    ontology['livestock_management'] = 0
    ontology['marine_technology'] = 0
    ontology['paper_technology'] = 0
    ontology['climate_change_and_the_environment'] = 0
    ontology['air_quality_management'] = 0
    ontology['ccmt'] = 0
    ontology['noise'] = 0
    ontology['soil'] = 0
    ontology['waste_management_and_recycling'] = 0
    ontology['water_and_wastewater'] = 0
    ontology['energy'] = 0
    ontology['carbon_footprint'] = 0
    ontology['energy_efficiency'] = 0
    ontology['low_carbon_technology'] = 0
    ontology['smart_cities_and_communities'] = 0
    ontology['health'] = 0
    ontology['active_ageing_and_self_management_of_health'] = 0
    ontology['preventing_disease'] = 0
    ontology['treating_and_managing_disease'] = 0
    ontology['e_health'] = 0
    ontology['health_biotechnology'] = 0
    ontology['health_care_provision_and_integrated_care'] = 0
    ontology['health_data'] = 0
    ontology['personalized_medicine'] = 0
    ontology['pharmaceuticals'] = 0
    ontology['social_care'] = 0
    ontology['security'] = 0
    ontology['catastrophe_fighting'] = 0
    ontology['digital_security'] = 0
    ontology['public_safety_communication'] = 0
    ontology['security_equipment'] = 0
    ontology['security_monitoring'] = 0
    ontology['society'] = 0
    ontology['european_culture'] = 0
    ontology['co_creation'] = 0
    ontology['education'] = 0
    ontology['employment'] = 0
    ontology['global_engagement'] = 0
    ontology['social_inequality'] = 0
    ontology['transport'] = 0
    ontology['aeronautics'] = 0
    ontology['automobiles'] = 0
    ontology['freight'] = 0
    ontology['intelligent_transport'] = 0
    ontology['maritime_transport'] = 0
    ontology['rail_transport'] = 0
    ontology['sustainable_transport'] = 0
    ontology['transport_infrastructure'] = 0
    ontology['urban_mobility'] = 0
    return ontology



def read_files(path):
    ann1files = [f for f in listdir(path) if isfile(join(path, f))]

    annotations = []

    for ann in ann1files:
        ontology = populate_ontology()
        content = ""
        if ".txt" in ann:
            if ".txt.ann1" in ann:
                continue
            objective = -1
            actors = -1
            outputs = -1
            innovativeness = -1
            si = -1
            f = open(path +'/'+ann,'r')
            lines = f.readlines()
            for line in lines:
                content = content + line
            f = open(path + "/" + ann.replace('.txt','.txt.ann1'), "r")
            lines = f.readlines()
            topics_s = False
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
                if "Topics" in line:
                    topics_s = True
                if topics_s:
                    if "Topics:" in line:
                        continue
                    if line.split('/')[-1].replace('\n','') in ontology.keys():
                        ontology[line.split('/')[-1].replace('\n','')]=1
                    if line.split('/')[-1].replace('\n','') in ["cultural_heritage","democracy","addressing_hate_speech_and_harassment","reflective_society"]:
                        ontology['european_culture'] = 1
                    if line.split('/')[-1].replace('\n','') in ["co_design","knowledge_transfer","user_involvement"]:
                        ontology['co_creation'] = 1
                    if line.split('/')[-1].replace('\n','') in ["entrepreneurial_education", "language_and_integration", "literacy"]:
                        ontology['education'] = 1
                    if line.split('/')[-1].replace('\n','') in ["job_search", "entrepreneurship", "work_conditions_and_work_environment"]:
                        ontology['employment'] = 1
                    if line.split('/')[-1].replace('\n','') in ["common_security_and_defence", "global_governance",
                                               "global_mobility"]:
                        ontology['global_engagement'] = 1
                    if line.split('/')[-1].replace('\n','') in ["gender_inequality", "poverty",
                                               "race_and_ethnic_inequality"]:
                        ontology['social_inequality'] = 1
                    if line.split('/')[-1].replace('\n','') in ["paper_technology","marine_technology","animals_livestock_management","landscape_management",
                                               "food_production","agricultural_biotechnology","food_sustainability"]:
                        ontology['bioeconomy']  = 1
                    if line.split('/')[-1].replace('\n','') in ["air_quality_management", "ccmt", "noise",
                                               "soil",
                                               "waste_management_and_recycling", "waste_management", "recycling","packaging",
                                               "water_and_wastewater"]:
                        ontology['climate_change_and_the_environment'] = 1
                    if line.split('/')[-1].replace('\n','') in ["carbon_footprint", "energy_efficiency", "integration_of_ict_and_energy",
                                               "energy_and_telecom_sector",
                                               "energy_in_buildings", "energy_in_industry", "heating_and_cooling",
                                               "low_carbon_technology",
                                               "smart_cities_and_communities","alternative_fuels","bio_fuels","carbon_capture_and_storage",
                                               "concentrated_solar_power","energy_storage","geothermal_energy","hydro_power","ocean_energy",
                                               "photovoltaics","renewable_heating_and_cooling","renewable_heating_and_cooling"]:
                        ontology['energy'] = 1
                    if line.split('/')[-1].replace('\n','') in ["active_ageing_and_self_management_of_health", "preventing_disease", "treating_and_managing_disease",
                                               "e_health",
                                               "health_biotechnology", "health_care_provision_and_integrated_care", "health_data","personalized_medicine",
                                               "pharmaceuticals","social_care"]:
                        ontology['health'] = 1
                    if line.split('/')[-1].replace('\n','') in ["catastrophe_fighting", "digital_security", "public_safety_communication",
                                               "security_equipment",
                                               "security_monitoring"]:
                        ontology['security'] = 1
                    if line.split('/')[-1].replace('\n','') in ["european_culture", "cultural_heritage", "democracy",
                                               "addressing_hate_speech_and_harassment",
                                               "reflective_society","co_creation","co_design","knowledge_transfer","user_involvement","education",
                                               "entrepreneurial_education","language_and_integration","literacy","employment","job_search",
                                               "entrepreneurship","work_conditions_and_work_environment","global_engagement","common_security_and_defence",
                                               "global_governance","global_mobility","social_inequality","gender_inequality","poverty","race_and_ethnic_inequality",
                                               ]:
                        ontology['society'] = 1
                    if line.split('/')[-1].replace('\n','') in ["aeronautics", "automobiles", "freight",
                                               "intelligent_transport",
                                               "maritime_transport","rail_transport","sustainable_transport","bio_fuels_for_transport",
                                               "transport_infrastructure","urban_mobility"]:
                        ontology['transport'] = 1



            annotations.append([ann,content,objective,actors,outputs,innovativeness,si,ontology])
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

    def train_LSTM_words_only(self,X_train,X_topics,y_train):
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
        model = Sequential()
        model1 = Sequential()
        model1.add(embedding_layer)
        model1.add(Dropout(0.2))
        model2 = Sequential()
        model2.add(Dense(50, activation='relu',input_shape=(50,)))
        model2.add(Dropout(0.2))
        model3 = Concatenate([model1,model2])
        model.add(model3,input_shape=(350,))
        model.add(Conv1D(filters=512, kernel_size=2, padding='same', activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=256, kernel_size=2, padding='same', activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=128, kernel_size=2, padding='same', activation='relu'))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(100)))
        model.add(Dropout(0.2))
        model.add(Dense(2))
        model.add(Dropout(0.2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit([data,X_topics], y_train,
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


    def predict_LSTM(self,X_test,topics):
        sequences = self.tokenizer.texts_to_sequences(X_test)
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        y_pred = self.clf.predict([data,topics])
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
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2"
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

    topics = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[2]
        if value>=2:
            value = 1
        else:
            value =0
        top = []
        for key in anns[7].keys():
            top.append(anns[7][key])
        topics.append(top)
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA,'topics':topics})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    print("Train DF:\n"+str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)
    #
    #
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                   replace=True,     # sample with replacement
    #                                   n_samples=420,    # to match majority class
    #                                   random_state=83293) # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled],ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled


    folder = sklearn.model_selection.KFold(5)
    i = 0
    for test_index,train_index in folder.split(train_df):
        i = i +1
        print("FOLD:"+str(i))
        cls = LSTMClassifier()
        X_train = train_df['text'][train_index]
        X_topics_train = train_df['topics'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_LSTM_words_only(X_train,X_topics_train,y_train)
        X_test= train_df['text'][test_index]
        X_topics_test = train_df['topics'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_LSTM(X_test,X_topics_test)
        cls.print_reports(y_pred, y_test)
    cls = LSTMClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_LSTM_words_only(X_train, y_train)
    cls.save_LSTM_model("Objectives_LSTM")
    y_pred = cls.predict_LSTM(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Objectives")

    ### Actors
    print("Working on Actors")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[3]
        if value>=2:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=350,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = LSTMClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_LSTM_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_LSTM(X_test)
        cls.print_reports(y_pred, y_test)
    cls = LSTMClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_LSTM_words_only(X_train, y_train)
    cls.save_LSTM_model("Actors_LSTM")
    y_pred = cls.predict_LSTM(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Actors")

    ### Outputs
    print("Working on Outputs")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[4]
        if value>=2:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=400,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = LSTMClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_LSTM_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_LSTM(X_test)
        cls.print_reports(y_pred, y_test)
    cls = LSTMClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_LSTM_words_only(X_train, y_train)
    cls.save_LSTM_model("Outputs_LSTM")
    y_pred = cls.predict_LSTM(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Outputs")

    ### Innovativeness
    print("Working on Innovativness")
    texts = []
    classA = []
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
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)


    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)
    # #
    # #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=400,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = LSTMClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_LSTM_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_LSTM(X_test)
        cls.print_reports(y_pred, y_test)
    cls = LSTMClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_LSTM_words_only(X_train, y_train)
    cls.save_LSTM_model("Innovativeness_LSTM")
    y_pred = cls.predict_LSTM(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Innovativeness")