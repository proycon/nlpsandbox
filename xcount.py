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

def addparentR(ngram, parent):        
    global parents
    if not (ngram in parents):
        parents[ngram] = []
    parents[ngram].append(parent) 
        
def totalparentoccurrence(ngram):
    global parents
    """Compute the occurrence of the parents"""        
    
    for parent in parents[ngram]:
        for parent2 in parents[ngram]:
            if parent != parent2:                
                if parent in parent2:
                    c = min(g.freqlist[parent], g.freqlist[parent2]
                    rel[(parent,parent2)] = c
                elif parent2 in parent:
                    rel[(parent,parent2)] = c
                else:
                    
        
    
        

g = PatternGraph2(sys.argv[1])
parents = {}

for ngram, count in g.freqlist.items():    
    for subgram in ngram.subngrams():
        if subgram in g.freqlist:
            addparent(subgram, ngram)
            

xcount = {}
n = g.max_n
while n > 0:
    for ngram, count in g.freqlist.items():
        if len(ngram) == n:
            if ngram in parents:
                superparents = []
                
                dep = {}
                  
                parentcount = 0                            
                for parent in parents[ngram]:
                    for parent2 in parents[ngram]:
                        if parent != parent2 and parent in parents and parent2 in parents:
                            superparents = set()
                            for superparent in parents[parent]:
                                for superparent2 in parents[parent2]:
                                    if superparent == superparent2:
                                        superparents.add(superparent)
                            if overlap:
                                if not parent in dep:
                                    dep[parent] = set()
                                dep[parent].add(parent2)
                
                processed = {}
                for parent in parents[ngram]:        
                    if parent in dep:                        
                        minoc = g.freqlist[parent]
                        for parent2 in dep[parent]:
                            if g.freqlist[parent2] < minoc:
                                minoc = g.freqlist[parent2]
                            processed[parent2] = True
                        parentcount += minoc
                        #print >>sys.stderr,"DEP '", str(parent) + "' ("+str(g.freqlist[parent])+ ") '" + str(parent2) + "'  ("+str(g.freqlist[parent2])+ ") = " +  str(minoc)
                    elif not (parent in processed):    
                        parentcount += g.freqlist[parent]                                        
                
                if parentcount > g.freqlist[ngram]:                        
                    print >>sys.stderr, "NEGATIVE result for " + str(ngram)
                    xcount[ngram] = 0
                else:
                    xcount[ngram] = g.freqlist[ngram] - parentcount
            else:
                xcount[ngram] = g.freqlist[ngram]
    n = n - 1
            
                
                
for ngram in g.freqlist:
    try:
        curparents = parents[ngram]
    except KeyError:
        curparents = []
    xfactor = xcount[ngram] / float(g.freqlist[ngram])
    print str(ngram) + "\t" + str(g.freqlist[ngram]) + "\t" + str(xcount[ngram]) + "\t" + str(xfactor) + "\t" +  " || ".join([ str(parent) + " (" + str(g.freqlist[parent]) +")"  for parent in curparents])
    


        

