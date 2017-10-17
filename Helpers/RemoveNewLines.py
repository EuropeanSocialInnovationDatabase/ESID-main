import re
from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir("ESID-data2") if isfile(join("ESID-data2", f))]
for file in onlyfiles:
    s = open("ESID-data2/"+file, 'r').read()
    s = re.sub(r'(\n\s*)+\n+', '\n\n', s)
    f = open("ESID-data2/"+file,'w')
    f.write(s)
    f.close()