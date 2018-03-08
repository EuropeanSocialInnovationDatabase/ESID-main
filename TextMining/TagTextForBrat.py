#!/usr/bin/env python
# -*- coding: utf-8 -*-
from NER.StanfordNER import StanfordTagger
import nltk
from os import listdir
import sys
from os.path import isfile, join
reload(sys)
sys.setdefaultencoding('utf8')
if __name__ == '__main__':
    path = "Cleaned_text"
    st = StanfordTagger('Resources')
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        f = open("Cleaned_text/"+file,"r")
        ann_name = file.replace(".txt",".ann")
        f_ann = open("Cleaned_text/" + ann_name, "w")
        text = f.read()
        f.close()
        print text
        tagged = st.tag_text(text.decode('utf-8'))
        position = 0
        pos_end = 0
        start = 0
        index = 1
        text = text.replace('\n','')
        for tag in tagged:
            if tag[1]=="ORGANIZATION":
                pos2 = text.find(tag[0],start)
                pos = text.index(str(tag[0]),start)
                position = pos
                start = position + len(tag[0])
                pos_end = position + len(tag[0])
                f_ann.write("T"+str(index)+"\t"+"Organisation"+" "+str(position)+" "+str(pos_end)+"\t"+tag[0]+'\n')
                index = index + 1
        f_ann.close()

    pass
