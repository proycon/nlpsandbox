#!/usr/bin/env python3
from __future__ import print_function, unicode_literals, division, absolute_import

import sys
import os.path
from collections import defaultdict
import glob
from pynlpl.formats import folia


def processfile(f, stats):
    print("Processing " + f,file=sys.stderr)
    try:
        doc = folia.Document(file=f)
    except:
        print("ERROR PARSING " + f + ", skipping",file=sys.stderr)
        return
    if doc.hasdeclaration(folia.Correction, "http://raw.github.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml"):
        stats['annotateddocs'] += 1
        stats['wordcount'] += len(doc.words())
        for correction in doc.select(folia.Correction):
            stats['correctioncount'] += 1
            if correction.cls:
                stats['byclass'][correction.cls] += 1
            if correction.annotator:
                stats['byannotator'][correction.annotator] += 1
    else:
        stats['unannotateddocs'] += 1


def processdir(d, stats):
    for f in glob.glob(d + '/*'):
        if os.path.isdir(f):
            processdir(f,stats)
        elif f[-10:] == '.folia.xml':
            processfile(f, stats)


stats = {'byclass': defaultdict(int), 'byannotator': defaultdict(int), 'annotateddocs':0, 'unannotateddocs':0 }

for f in sys.argv[1:]:
    if os.path.isdir(f):
        processdir(f,stats)
    else:
        processfile(f, stats)


print("annotated documents = " + "\t" + str(stats['annotateddocs']))
print("unannotated documents =" + "\t" + str(stats['unannotateddocs']))
print("total words = " + "\t" + str(stats['wordcount']))
print("total corrections = " + "\t" + str(stats['correctioncount']))

print("BY CLASS")
for cls, count in sorted(stats['byclass'].items(), key= lambda x: x[1] * -1 ):
    print(cls + "\t" + str(count))

print()
print("BY ANNOTATOR")
for annotator, count in sorted(stats['byannotator'].items(), key= lambda x: x[1] * -1 ):
    print(annotator + "\t" + str(count))



