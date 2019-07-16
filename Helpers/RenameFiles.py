from os import listdir
from os.path import isfile,join
import os

folder = "KickStarter/"
onlyfiles = [f for f in listdir(folder) if isfile(join(folder,f))]
i = 1
for file in onlyfiles:
    if ".txt" in file:
        os.rename(folder+file,folder+str(i)+os.path.splitext(file)[1])
        os.rename(folder + file.replace(".txt",".ann"), folder + str(i) + ".ann")
        i = i+1
