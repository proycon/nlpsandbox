#!/usr/bin/env python3

import sys
from collections import defaultdict
from urllib.parse import quote_plus


log = open(sys.argv[1],'r',encoding='utf-8')

persentencescore = {}
with open(sys.argv[2],'r') as f:
    for line in f:
        if line.strip():
            sentence,_,wac,_ = line.split("\t")
            persentencescore[int(sentence)] = float(wac)


def countclasses(filename):
    classes= defaultdict(int)
    with open(filename,'r',encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                fields = line.split("\t")
                classes[fields[-1]] += 1
    return len(classes)

expertclasses = {}
classesaccuracy = defaultdict(list)
classifierdir = sys.argv[3]


for line in log:
    line = line.strip()
    if line:
        if line[:10] == "Sentence #":
            sentence = int(line[10:])
            print("Sentence #" + str(sentence),file=sys.stderr)
        if line[:13] == "Classifying '":
            end = line.find("' ...")
            expert = line[13:end]
            print("Expert: " + expert,file=sys.stderr)
            if not expert in expertclasses:
                classes = expertclasses[expert] = countclasses(classifierdir + '/' + quote_plus(expert) + '.train')
            else:
                classes = expertclasses[expert]
            classesaccuracy[classes].append( persentencescore[sentence])

classesaccuracy_norm = { c: sum(classesaccuracy[c]) / len(classesaccuracy[c]) for c in classesaccuracy }
print(classesaccuracy_norm)
for k,v in sorted(classesaccuracy_norm.items()):
    print(k, v, len(classesaccuracy[k]))
