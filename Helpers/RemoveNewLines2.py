import re
from os import listdir
from os.path import isfile, join
import os
import nltk
if not os.path.exists("SI-Drive-otherroung_filtered2"):
    os.makedirs("SI-Drive-otherroung_filtered2")
output_dir = "SI-Drive-otherroung_filtered2"
onlyfiles = [f for f in listdir("SI-Drive-otherround") if isfile(join("SI-Drive-otherround", f)) and ".txt" in f.lower()]
for file in onlyfiles:
    print "Working on "+file
    f = open("SI-Drive-otherround/"+file,"r")
    lines = f.readlines()
    flines = []
    for l in lines:
        notRepeated = True
        for a in flines:
            if l.strip()==a.strip():
                notRepeated = False
        if notRepeated:
            flines.append(l.strip())
    output = open(output_dir+"/"+file.lower(),"w")
    for l in flines:
        output.write(l+"\r\n")
    output.close()
    f.close()
    ann = open(output_dir+"/"+file.lower().replace(".txt",".ann"),"w")
    ann.close()
print "done"

