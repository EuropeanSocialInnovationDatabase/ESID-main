from os import listdir
from os.path import isfile, join,isdir

path_to_annotations = '/home/mbaxknm4/Software/brat-v1.3_Crunchy_Frog/data/AnnotationWorkshop/'
annotators = [f for f in listdir(path_to_annotations) if isdir(join(path_to_annotations, f))]
print annotators
files = {}
all_files = []
for ann in annotators:
    print ann
    files[ann] = [f for f in listdir(path_to_annotations+ann) if isfile(join(path_to_annotations+ann, f)) and f.endswith('.txt')]
    all_files.extend(files[ann])
    print files[ann]
print len(all_files)
print set(all_files)
print len(set(all_files))
annotated_count = {}
for file in set(all_files):
    annotated_count[file] = 0
    for ann in annotators:
        if file in files[ann]:
            annotated_count[file] = annotated_count[file]  + 1
count_double_annotated = 0
for file in set(all_files):
    if annotated_count[file]>=2:
        count_double_annotated = count_double_annotated + 1
    print  file + " : "+ str(annotated_count[file])
print count_double_annotated

