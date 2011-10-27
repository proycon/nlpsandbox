#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.formats import folia
import sys

data = []
f = open('/home/proycon/exp/idiomen.csv','r')
for i, line in enumerate(f.readlines()):
    fields = line.strip().split('\t')
    if i > 1 and len(fields) > 4:
        data.append( sum([fields[1].split(' '), fields[2].split(' '), fields[3].split(' ') ],[]) ) 
f.close()

for doc in folia.Corpus(sys.argv[1],'pos'):
    print >>sys.stderr, "Processing " + doc.filename
    for sentence in doc.sentences():    
        for i, idiom in enumerate(data):
            match = [False] * len(idiom)            
            for word in sentence.words():
                for j, idiomword in enumerate(idiom):
                    if word.lemma() == idiomword:
                        match[j] = word.id
            
            if all(match): 
                s = str(i+1) + "\t" + ";".join(idiom) +  "\t" + unicode(sentence)
                print s.encode('utf-8')
                        
