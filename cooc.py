#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

sourcefile = sys.argv[1]
targetfile = sys.argv[2]


def loadindex(filename):
    index = {}
    with open(sourcefile) as f:
        for line in f:
            fields = line.split('\t')        
            if len(fields) == 2:
                index[fields[0]] = set(( int(x) for x in fields[1].strip().split(' ')))
    return index
    

print >>sys.stderr,"Loading source index"    
sourceindex = loadindex(sourcefile)
print >>sys.stderr,"Loading target index"
targetindex = loadindex(targetfile)

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

            
        
        
            
            
       

        
        
        
        
        
        
        
