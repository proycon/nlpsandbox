#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from pynlpl.textprocessors import MultiWindower

sourcefile = sys.argv[1]
targetfile = sys.argv[2]

def makeindex(filename):
    index = {}
    with open(filename) as f:
        for i, line in enumerate(f):
            if line:
                words = line.strip().split(' ')
                for ngram in MultiWindower(words,1,8):
                    if ngram in index:
                        index[ngram].add(i)
                    else:
                        index[ngram] = set( (i,) )
    return index
    

print >>sys.stderr,"Computing source index"    
sourceindex = makeindex(sourcefile)
print >>sys.stderr,"Computing target index"
targetindex = makeindex(targetfile)

print len(sourceindex)
print len(targetindex)

jaccard = {}

for source in sourceindex:
    maxcooc = 0    
    jaccard = {}
    for target in targetindex:
        jaccard[target] = len(sourceindex[source] & targetindex[target]) / float(len(sourceindex[source] | targetindex[target])) #intersection / union
        if jaccard[target] > maxcooc:
            maxcooc = jaccard[target]
                
    for target in jaccard:
        if jaccard[target] == maxcooc:
            print repr(source) + '\t' + repr(target) + '\t' + str(jaccard[target])

            
        
        
            
            
       

        
        
        
        
        
        
        
