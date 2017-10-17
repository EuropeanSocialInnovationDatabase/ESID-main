import os

for filename in os.listdir('.'):
    if filename.startswith("p_"):
        parts1 = filename.split("_")
        p_part = parts1[0]
        rest = parts1[1]
        parts2 = rest.split(".")
        doc_num = parts2[0]
        extension = parts2[1]
        len_doc_num = len(doc_num)
        if(len_doc_num==1):
            doc_num = "000"+doc_num
        if (len_doc_num == 2):
            doc_num = "00" + doc_num
        if (len_doc_num == 3):
            doc_num = "0" + doc_num
        print "p_"+doc_num+"."+extension
        os.rename(filename, "p_"+doc_num+"."+extension)