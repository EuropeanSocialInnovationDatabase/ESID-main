from os import listdir
from os.path import isfile, join,isdir
import csv
import re
import sklearn.metrics
from keras.callbacks import EarlyStopping
from keras import Input
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Conv1D, MaxPooling1D, Flatten,Conv2D
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import gensim
import os
import numpy as np
import time
from keras import backend as K

from keras_text.data import Dataset
from keras_text.models import TokenModelFactory
from keras_text.models import YoonKimCNN, AttentionRNN, StackedRNN
from keras_text.processing import WordTokenizer



def mcor(y_true, y_pred):
    # matthews_correlation
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos

    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos

    tp = K.sum(y_pos * y_pred_pos)
    tn = K.sum(y_neg * y_pred_neg)

    fp = K.sum(y_neg * y_pred_pos)
    fn = K.sum(y_pos * y_pred_neg)

    numerator = (tp * tn - fp * fn)
    denominator = K.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    return numerator / (denominator + K.epsilon())


def precision(y_true, y_pred):
    """Precision metric.

    Only computes a batch-wise average of precision.

    Computes the precision, a metric for multi-label classification of
    how many selected items are relevant.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def recall(y_true, y_pred):
    """Recall metric.

    Only computes a batch-wise average of recall.

    Computes the recall, a metric for multi-label classification of
    how many relevant items are selected.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2 * ((precision * recall) / (precision + recall))

class DataSet:
    Annotators = []
    def __init__(self):
        self.Annotators = []

class Annotator:
    files = []
    documents = []
    Name = ""
    def __init__(self):
        self.files = []
        self.documents = []
        self.Name = ""

class Document:
    Lines = []
    DocumentName = ""
    DatabaseID = ""
    Annotations = []
    Text = ""
    isSpam = False
    Project_Mark_Objective_1A = 0
    Project_Mark_Objective_1B = 0
    Project_Mark_Objective_1C = 0
    Project_Mark_Actors_2A = 0
    Project_Mark_Actors_2B = 0
    Project_Mark_Actors_2C = 0
    Project_Mark_Outputs_3A = 0
    Project_Mark_Innovativeness_3A = 0

    isProjectObjectiveSatisfied = False
    isProjectActorSatisfied = False
    isProjectOutputSatisfied = False
    isProjectInnovativenessSatisfied = False

    isProjectObjectiveSatisfied_predicted = False
    isProjectActorSatisfied_predicted = False
    isProjectOutputSatisfied_predicted = False
    isProjectInnovativenessSatisfied_predicted = False

    def __init__(self):
        self.Text = ""
        self.Lines = []
        self.DocumentName = ""
        self.DatabaseID = ""
        self.Annotations = []
        self.isSpam = False
        self.Project_Mark_Objective_1A = 0
        self.Project_Mark_Objective_1B = 0
        self.Project_Mark_Objective_1C = 0
        self.Project_Mark_Actors_2A = 0
        self.Project_Mark_Actors_2B = 0
        self.Project_Mark_Actors_2C = 0
        self.Project_Mark_Outputs_3A = 0
        self.Project_Mark_Innovativeness_3A = 0
        self.Project_Mark_Innovativeness_3A = 0
        self.isProjectObjectiveSatisfied = False
        self.isProjectActorSatisfied = False
        self.isProjectOutputSatisfied = False
        self.isProjectInnovativenessSatisfied = False

        self.isProjectObjectiveSatisfied_predicted = False
        self.isProjectActorSatisfied_predicted = False
        self.isProjectOutputSatisfied_predicted = False
        self.isProjectInnovativenessSatisfied_predicted = False


class Line:
    StartSpan = 0
    EndSpan = 0
    Text = ""
    Sentences = []
    Tokens = []
    Annotations = []
    def __init__(self):
        self.StartSpan = 0
        self.EndSpan = 0
        self.Text = ""
        self.Sentences = []
        self.Tokens = []
        self.Annotations = []


class Sentence:
    SentenceText = ""
    StartSpan = -1
    EndSpan = -1
    Annotations = []
    def __init__(self):
        self.SentenceText = ""
        self.StartSpan = -1
        self.EndSpan = -1
        self.Annotations = []

class Annotation:
    FromFile = ""
    FromAnnotator = ""
    AnnotationText = ""
    StartSpan = -1
    EndSpan = -1
    HighLevelClass = ""
    LowLevelClass = ""

if __name__ == '__main__':
    os.environ['PYTHONHASHSEED'] = '4'
    np.random.seed(523)
    max_words = 20000
    batch_size = 32
    epochs =100
    GLOVE_DIR = "../../../Helpers/BratDataProcessing/Glove_dir"
    MAX_SEQUENCE_LENGTH = 1100
    EMBEDDING_DIM = 50
    data_folder = "../../../Helpers/FullDataset_Alina"
    ds = DataSet()
    total_num_spam = 0
    sentences = []
    total_num_files = 0
    #job = aetros.backend.start_job('nikolamilosevic86/GloveModel')
    annotators = [f for f in listdir(data_folder) if isdir(join(data_folder, f))]
    for ann in annotators:
        folder = data_folder+"/"+ann
        Annot = Annotator()
        Annot.Name = ann
        ds.Annotators.append(Annot)
        onlyfiles = [f for f in listdir(folder) if (f.endswith(".txt"))]
        for file in onlyfiles:
            Annot.files.append(data_folder+"/"+ann+'/'+file)
            doc = Document()
            total_num_files = total_num_files + 1
            doc.Lines = []
            #doc.Annotations = []
            doc.DocumentName= file
            Annot.documents.append(doc)
            if(file.startswith('a') or file.startswith('t')):
                continue
            print file
            doc.DatabaseID = file.split("_")[1].split(".")[0]
            fl = open(data_folder+"/"+ann+'/'+file,'r')
            content = fl.read()
            doc.Text = content
            lines = content.split('\n')
            line_index = 0
            for line in lines:
                l = Line()
                l.StartSpan = line_index
                l.EndSpan = line_index+len(line)
                l.Text = line
                line_index = line_index+len(line)+1
                sentences.append(line)
                doc.Lines.append(l)


            an = open(data_folder+"/"+ann+'/'+file.replace(".txt",".ann"),'r')
            annotations = an.readlines()
            for a in annotations:
                a = re.sub(r'\d+;\d+','',a).replace('  ',' ')
                split_ann = a.split('\t')
                if (split_ann[0].startswith("T")):
                    id = split_ann[0]
                    sp_split_ann = split_ann[1].split(' ')
                    low_level_ann = sp_split_ann[0]
                    if low_level_ann=="ProjectMark":
                        continue
                    span_start = sp_split_ann[1]
                    span_end = sp_split_ann[2]
                    ann_text = split_ann[2]
                    Ann = Annotation()
                    Ann.AnnotationText = ann_text
                    Ann.StartSpan = int(span_start)
                    Ann.EndSpan = int(span_end)
                    Ann.FromAnnotator = Annot.Name
                    Ann.FromFile = file
                    Ann.LowLevelClass = low_level_ann
                    if(low_level_ann == "SL_Outputs_3a"):
                        Ann.HighLevelClass = "Outputs"
                    if (low_level_ann == "SL_Objective_1a" or low_level_ann == "SL_Objective_1b" or low_level_ann == "SL_Objective_1c"):
                        Ann.HighLevelClass = "Objectives"
                    if (low_level_ann == "SL_Actors_2a" or low_level_ann == "SL_Actors_2b" or low_level_ann == "SL_Actors_2c"):
                        Ann.HighLevelClass = "Actors"
                    if (low_level_ann == "SL_Innovativeness_4a"):
                        Ann.HighLevelClass = "Innovativeness"
                    doc.Annotations.append(Ann)
                    for line in doc.Lines:
                        if line.StartSpan<=Ann.StartSpan and line.EndSpan>=Ann.EndSpan:
                            line.Annotations.append(Ann)
                else:
                    id = split_ann[0]
                    sp_split_ann = split_ann[1].split(' ')
                    mark_name = sp_split_ann[0]
                    if (len(sp_split_ann)<=2):
                        continue
                    mark = sp_split_ann[2].replace('\n','')
                    if(mark_name=="DL_Outputs_3a"):
                        doc.Project_Mark_Outputs_3A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectOutputSatisfied = True
                    if (mark_name == "DL_Objective_1a"):
                        doc.Project_Mark_Objective_1A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Objective_1b"):
                        doc.Project_Mark_Objective_1B = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Objective_1c"):
                        doc.Project_Mark_Objective_1C = int(mark)
                        if int(mark)>=2:
                            doc.isProjectObjectiveSatisfied = True
                    if (mark_name == "DL_Innovativeness_4a"):
                        doc.Project_Mark_Innovativeness_3A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectInnovativenessSatisfied = True
                    if (mark_name == "DL_Actors_2a"):
                        doc.Project_Mark_Actors_2A = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Actors_2b"):
                        doc.Project_Mark_Actors_2B = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
                    if (mark_name == "DL_Actors_2c"):
                        doc.Project_Mark_Actors_2C = int(mark)
                        if int(mark)>=2:
                            doc.isProjectActorSatisfied = True
            if(doc.Project_Mark_Objective_1A==0 and doc.Project_Mark_Objective_1B == 0 and doc.Project_Mark_Objective_1C==0 and doc.Project_Mark_Actors_2A==0
                and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2B==0 and doc.Project_Mark_Actors_2C==0 and doc.Project_Mark_Outputs_3A == 0
                and doc.Project_Mark_Innovativeness_3A==0):
                doc.isSpam = True
                total_num_spam = total_num_spam + 1

    with open('annotations.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        for ann in ds.Annotators:
            for doc in ann.documents:
                for annot in doc.Annotations:
                    spamwriter.writerow([annot.FromFile,annot.FromAnnotator,annot.AnnotationText,annot.LowLevelClass,annot.HighLevelClass,annot.StartSpan,annot.EndSpan])
    i = 0
    j = i+1
    kappa_files = 0

    done_documents = []
    num_overlap_spam = 0
    num_spam = 0

    total_objectives = 0
    total_outputs = 0
    total_actors = 0
    total_innovativeness = 0
    ann1_annotations_objectives = []
    ann2_annotations_objectives = []
    ann1_annotations_actors = []
    ann2_annotations_actors = []
    ann1_annotations_outputs = []
    ann2_annotations_outputs = []
    ann1_annotations_innovativeness = []
    ann2_annotations_innovativeness = []
    match_objectives = 0
    match_outputs = 0
    match_actors = 0
    match_innovativeness = 0

    while i<len(ds.Annotators)-1:
        while j<len(ds.Annotators):
            annotator1 = ds.Annotators[i]
            annotator2 = ds.Annotators[j]
            for doc1 in annotator1.documents:
                for doc2 in annotator2.documents:
                    if doc1.DocumentName == doc2.DocumentName and doc1.DocumentName not in done_documents:
                        done_documents.append(doc1.DocumentName)
                        line_num = 0

                        ann1_objective = [0] * len(doc1.Lines)
                        ann2_objective = [0] * len(doc2.Lines)
                        ann1_output = [0] * len(doc1.Lines)
                        ann2_output = [0] * len(doc2.Lines)
                        ann1_actor = [0] * len(doc1.Lines)
                        ann2_actor = [0] * len(doc2.Lines)
                        ann1_innovativeness = [0] * len(doc1.Lines)
                        ann2_innovativeness = [0] * len(doc2.Lines)
                        while line_num<len(doc1.Lines):
                            if len(doc1.Lines[line_num].Annotations)>0:
                                for a in doc1.Lines[line_num].Annotations:
                                    if a.HighLevelClass == "Objectives":
                                        ann1_objective[line_num] = 1
                                        total_objectives = total_objectives + 1
                                    if a.HighLevelClass == "Outputs":
                                        ann1_output[line_num] = 1
                                        total_outputs = total_outputs + 1
                                    if a.HighLevelClass == "Actors":
                                        ann1_actor[line_num] = 1
                                        total_actors = total_actors + 1
                                    if a.HighLevelClass == "Innovativeness":
                                        ann1_innovativeness[line_num] = 1
                                        total_innovativeness = total_innovativeness + 1
                                    for a1 in doc2.Lines[line_num].Annotations:
                                        if a1.HighLevelClass == a.HighLevelClass:
                                            if a1.HighLevelClass == "Objectives":
                                                match_objectives = match_objectives + 1
                                            if a1.HighLevelClass == "Outputs":
                                                match_outputs = match_outputs + 1
                                            if a1.HighLevelClass == "Actors":
                                                match_actors = match_actors + 1
                                            if a1.HighLevelClass == "Innovativeness":
                                                match_innovativeness = match_innovativeness + 1
                            if len(doc2.Lines[line_num].Annotations)>0:
                                for a in doc2.Lines[line_num].Annotations:
                                    if a.HighLevelClass == "Objectives":
                                        ann2_objective[line_num] = 1
                                        total_objectives = total_objectives + 1
                                    if a.HighLevelClass == "Outputs":
                                        ann2_output[line_num] = 1
                                        total_outputs = total_outputs + 1
                                    if a.HighLevelClass == "Actors":
                                        ann2_actor[line_num] = 1
                                        total_actors = total_actors + 1
                                    if a.HighLevelClass == "Innovativeness":
                                        ann2_innovativeness[line_num] = 1
                                        total_innovativeness = total_innovativeness + 1
                            line_num = line_num + 1
                        ann1_annotations_outputs.extend(ann1_output)
                        ann2_annotations_outputs.extend(ann2_output)
                        ann1_annotations_objectives.extend(ann1_objective)
                        ann2_annotations_objectives.extend(ann2_objective)
                        ann1_annotations_actors.extend(ann1_actor)
                        ann2_annotations_actors.extend(ann2_actor)
                        ann1_annotations_innovativeness.extend(ann1_innovativeness)
                        ann2_annotations_innovativeness.extend(ann2_innovativeness)
                        kappa_outputs = sklearn.metrics.cohen_kappa_score(ann1_output,ann2_output)
                        kappa_objectives = sklearn.metrics.cohen_kappa_score(ann1_objective, ann2_objective)
                        kappa_actors = sklearn.metrics.cohen_kappa_score(ann1_actor, ann2_actor)
                        kappa_innovativeness = sklearn.metrics.cohen_kappa_score(ann1_innovativeness, ann2_innovativeness)
                        print "Statistics for document:"+doc1.DocumentName
                        print "Annotators "+annotator1.Name+" and "+annotator2.Name
                        print "Spam by "+annotator1.Name+":"+str(doc1.isSpam)
                        print "Spam by " + annotator2.Name + ":" + str(doc2.isSpam)
                        if(doc1.isSpam == doc2.isSpam):
                            num_overlap_spam = num_overlap_spam+1
                        if doc1.isSpam:
                            num_spam = num_spam + 1
                        if doc2.isSpam:
                            num_spam = num_spam + 1
                        print "Cohen Kappa for class Objectives: "+str(kappa_objectives)
                        print "Cohen Kappa for class Actors: " + str(kappa_actors)
                        print "Cohen Kappa for class Outputs: " + str(kappa_outputs)
                        print "Cohen Kappa for class Innovativeness: " + str(kappa_innovativeness)
                        print "------------------------------------------------------------------"
                        kappa_files = kappa_files +1
            j = j+1
        i = i+1
        j = i+1

    print annotators
    doc_array = []
    text_array = []
    objectives = []
    actors = []
    outputs = []
    innovativeness = []
    for ann in ds.Annotators:
        for doc in ann.documents:
            doc_array.append([doc.Text,doc.isProjectObjectiveSatisfied,doc.isProjectActorSatisfied,doc.isProjectOutputSatisfied,doc.isProjectInnovativenessSatisfied])
            objectives.append(doc.isProjectObjectiveSatisfied)
            actors.append(doc.isProjectActorSatisfied)
            outputs.append(doc.isProjectOutputSatisfied)
            innovativeness.append(doc.isProjectInnovativenessSatisfied)
            text_array.append(doc.Text)
    tokenizer = Tokenizer(num_words=max_words)
    tokenizer.fit_on_texts(text_array)
    sequences = tokenizer.texts_to_sequences(text_array)

    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))

    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

    labels = to_categorical(np.asarray(actors))
    print('Shape of data tensor:', data.shape)
    print('Shape of label tensor:', labels.shape)

    # split the data into a training set and a validation set
    indices = np.arange(data.shape[0])
    data = data[indices]
    labels = labels[indices]
    nb_validation_samples = int(0.33 * data.shape[0])
    # x_train = data
    # y_train = labels
    total_precision = 0.0
    total_recall = 0.0
    total_fscore = 0.0
    embeddings_index = {}
    f = open(os.path.join(GLOVE_DIR, 'glove.6B.50d.txt'))
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()

    print('Found %s word vectors.' % len(embeddings_index))
    embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector
    embedding_layer = Embedding(len(word_index) + 1,
                                EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=MAX_SEQUENCE_LENGTH,
                                trainable=False)
    Total_TP = 0
    Total_FP = 0
    Total_FN = 0

    ds = Dataset(data, labels, tokenizer=tokenizer)
    #ds.update_test_indices(test_size=0.2)
    ds.save('dataset')
    tokenizer1 = WordTokenizer()
    t_array = []
    for text in text_array:
        t = unicode(text,errors='ignore')
        t_array.append(t)
    tokenizer1.build_vocab(t_array)
    # RNN models can use `max_tokens=None` to indicate variable length words per mini-batch.
    factory = TokenModelFactory(1, tokenizer1.token_index, max_tokens=100, embedding_type='glove.6B.100d')
    word_encoder_model = YoonKimCNN()
    model = factory.build_model(token_encoder_model=word_encoder_model)
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    model.summary()
    print("Traning Model...")
    print str(ds.X.shape)

    model.fit(data[ds.train_indices], labels[ds.train_indices], batch_size=batch_size, epochs=epochs, verbose=1,
              validation_data=(data[ds.test_indices], labels[ds.test_indices]))