import os
from os import listdir
from os.path import isfile, join
mypath = "../../../Helpers/Dataset_after_May/ZSI2"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for f in onlyfiles:
    if "p_" not in f:
        os.rename(mypath+"/"+f, mypath+"/p_"+f)