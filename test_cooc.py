#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

sourcefile = sys.argv[1]
targetfile = sys.argv[2]

def makeindex(filename):
    index = {}
    with open(filename) as f:
        for i, line in enumerate(f):
            if line:
                words = line.strip().split(' ')
                for word in words:
                    if word in index:
                        index[word].add(i)
                    else:
                        index[word] = set( (i,) )
    return index
    

print >>sys.stderr,"Computing source index"    
sourceindex = makeindex(sourcefile)
print >>sys.stderr,"Computing target index"
targetindex = makeindex(targetfile)

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
            print source + '\t' + target + '\t' + str(jaccard[target])

            
        
        
            
            
       

        
        
        
        
        
        
        
