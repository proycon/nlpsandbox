#!/usr/bin/env python3

import sys
from collections import defaultdict
from urllib.parse import quote_plus
import scipy.stats
import re


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
entropyaccuracy = []
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
        if line.startswith("Moses input:"):
            match = re.search('prob="([0-9\.\|]+)"', line)
            if match:
                probs = [ float(x) for x in match.group(1).split('||') ]
                entropy = scipy.stats.entropy(probs)
                print("Entropy=",entropy,file=sys.stderr)
                entropyaccuracy.append( (entropy, persentencescore[sentence]) )

classesaccuracy_norm = { c: sum(classesaccuracy[c]) / len(classesaccuracy[c]) for c in classesaccuracy }
print(classesaccuracy_norm)
for k,v in sorted(classesaccuracy_norm.items()):
    print(k, v, len(classesaccuracy[k]))

import matplotlib.pyplot as plt
import matplotlib2tikz
from pylab import polyfit, polyval


entropyaccuracy.sort()

plt.rc('text', usetex=True)
plt.rc('font', family='times')
a,b,r,p,std_err = scipy.stats.linregress([ x[0] for x in entropyaccuracy], [x[1] for x in entropyaccuracy])
print("Linear regression: r",r,'p',p,'std_err',std_err, file=sys.stderr)
y = polyval([a,b], [ x[0] for x in entropyaccuracy ])

plt.scatter([ x[0] for x in entropyaccuracy], [x[1] for x in entropyaccuracy])
plt.plot([ x[0] for x in entropyaccuracy], y)
plt.xlabel("Entropy", fontsize=11)
plt.ylabel("Word Accuracy", fontsize=11)
plt.xlim(-0.2,5)
plt.ylim(-0.04,1.04)
plt.savefig("entropyaccuracy.png", dpi=600)
#matplotlib2tikz.save('entropyaccuracy.tikz',figureheight = '\\figureheight', figurewidth = '\\figurewidth')

