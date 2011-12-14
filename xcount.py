#!/usr/bin/env python
#-*- coding:utf-8 -*-

from patterngraph import PatternGraph2
import sys

def addparent(ngram, parent):
    global parents
    if not (ngram in parents):
        parents[ngram] = []
    
    add = True
    for i, subgram in enumerate(parents[ngram]):
        if subgram != parent:
            if parent in subgram: #current ngram is smaller than the one known, replace                
                #print >>sys.stderr, "smaller parent found, '" + str(ngram) + "' overrides '" + str(subgram) +  "'. Replacing..."
                del parents[ngram][i]
                add = True
            elif subgram in parent: #already subsumed by smaller parent: ignore
                #print >>sys.stderr, "already subsumed by smaller parent"
                add = False
        else: 
            add = False
            
    if add:
        parents[ngram].append(parent) 
        

g = PatternGraph2(sys.argv[1])
parents = {}

for ngram, count in g.freqlist.items():    
    for subgram in ngram.subngrams():
        if subgram in g.freqlist:
            addparent(subgram, ngram)
                
                
for ngram, parents in parents.items():
    print str(ngram) + "\t" + " || ".join([ str(parent) for parent in parents])
    
            

        

