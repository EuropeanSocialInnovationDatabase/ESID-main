# encoding=utf8
import sys
from nltk.corpus import wordnet as wn
from os import listdir
from os.path import isfile, join,isdir
from nltk.stem import WordNetLemmatizer
import nltk
import  os
#reload(sys)
sys.setdefaultencoding('utf8')
wordnet_lemmatizer = WordNetLemmatizer()
print(wordnet_lemmatizer.lemmatize('dogs'))


PATH_good = "../Helpers/BratDataProcessing/WekaDataSet/Actor/Good"
PATH_bad = "../Helpers/BratDataProcessing/WekaDataSet/Actor/Bad"
directory1 = "../Helpers/BratDataProcessing/WekaDataSet/Actor/Bad_preprocessed"
if not os.path.exists(directory1):
    os.makedirs(directory1)

directory2 = "../Helpers/BratDataProcessing/WekaDataSet/Actor/Good_preprocessed"
if not os.path.exists(directory2):
    os.makedirs(directory2)
onlyfiles = [f for f in listdir(PATH_good) if (f.endswith(".txt"))]
for file in onlyfiles:
    print(file)
    fl = open(PATH_good + '/' + file, 'r')
    content = fl.read()
    tokens = nltk.word_tokenize(content)
    new_content = ""
    for token in tokens:
        t = wordnet_lemmatizer.lemmatize(unicode(token,errors='ignore'))
        synsets = wn.synsets(t)
        for synset in synsets:
            for lemma in synset.lemmas():
                new_content = new_content+" "+ lemma.name()
        new_content = new_content+" "+token
    f2 = open(directory2 + '/' + file, 'w')
    f2.write(new_content)
    f2.close()
    fl.close()

onlyfiles = [f for f in listdir(PATH_bad) if (f.endswith(".txt"))]
for file in onlyfiles:
    print(file)
    fl = open(PATH_bad + '/' + file, 'r')
    content = fl.read()
    tokens = nltk.word_tokenize(content)
    new_content = ""
    for token in tokens:
        t = wordnet_lemmatizer.lemmatize(unicode(token,errors='ignore'))
        synsets = wn.synsets(t)
        for synset in synsets:
            for lemma in synset.lemmas():
                new_content = new_content+" "+ lemma.name()
        new_content = new_content + " " + token
    f2 = open(directory1 + '/' + file, 'w')
    f2.write(new_content)
    f2.close()
    fl.close()

print(wn.synsets('innovative'))