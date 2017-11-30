from os import listdir
from os.path import isfile,join

folder = "Conflicts"
onlyfiles = [f for f in listdir(folder) if isfile(join(folder,f))]
for file in onlyfiles:
    ann_file = file.replace(".txt",".ann")
    ann = open(folder+"/"+ann_file,"w")
    ann.close()
