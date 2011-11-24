#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

from pynlpl.textprocessors import Classer
from pynlpl.statistics import FrequencyList

import sys
sourcecorpus = sys.argv[1]
targetcorpus = sys.argv[2]


CONVERGEDVALUE = 0.0001
MAXROUNDS = 250

sentencepairs = []
source = open(sourcecorpus,'r')
target = open(targetcorpus,'r')
while True:
    sourcesentence = source.readline()
    targetsentence = target.readline()
    if not sourcesentence or not targetsentence:
        break
    sourcesentence = sourcesentence.strip().split(' ') 
    targetsentence = targetsentence.strip().split(' ')
    sentencepairs.append( (sourcesentence, targetsentence) )
source.close()
target.close()


#initialise
count = {}
totalcount = {}
for ws in sourcesentence:
    totalcount[ws] = 0
    for wt in targetsentence:
        count[(wt,ws)] = 0  #count(wt|ws)


transprob = {}
stotal = {}
converged = False
i = 0


#Initialise uniformly
for j, (sourcesentence, targetsentence) in enumerate(sentencepairs):
    for ws in sourcesentence:
        v = 1 /float(len(targetsentence))
        for wt in targetsentence:
            transprob[(wt,ws)] = v
    
    
prevavdivergence = 99999    
while not converged:
    i += 1 
    print "Round " + str(i)

    total = {}
    
    
    converged = True
    totaldivergence = 0
    c = 0 
    for j, (sourcesentence, targetsentence) in enumerate(sentencepairs):
        if j % 10000 == 0: 
            print "\t@" + str(j+1)
        #compute sentencetotal for normalisation 
        stotal = {}
        for wt in targetsentence:    
            stotal[wt] = sum( ( transprob[(wt,ws)] for ws in sourcesentence if (wt,ws) in transprob ) )        
        
        #print "sentencetotal(targetword) for normalisation:"
        #print stotal
    
        count = {}        
        #collect counts
        for wt in targetsentence:
            for ws in sourcesentence:
                try:
                    value =  transprob[(wt,ws)] / float(stotal[wt])
                except KeyError:
                    value = 0
                    continue #no problem
                try:
                    count[(wt,ws)] += value 
                except KeyError:
                    count[(wt,ws)] = value 
                try:
                    total[ws] += value 
                except KeyError:
                    total[ws] = value
            
        
        #estimate probabilities
        for wt in targetsentence:
            for ws in sourcesentence:
                try:
                    prevtransprob = transprob[(wt,ws)]
                except KeyError:
                    prevtransprob = 0
                try:
                    newtransprob = count[(wt,ws)] / float(total[ws])
                    transprob[(wt,ws)] = newtransprob
                except KeyError:
                    newtransprob = 0              
                divergence = abs(newtransprob - prevtransprob)
                totaldivergence += divergence
                c += 1
    
    print "Translation probabilities p(targetword|sourceword) : "
    for targetword, sourceword in sorted(transprob):
         print "\tp("+targetword+"|"+sourceword+") = " + str(transprob[(targetword,sourceword)])    
    
    avdivergence = totaldivergence / float(c)
    print "\tTotal average divergence: " + str(avdivergence)
    if i >= MAXROUNDS or abs(avdivergence - prevavdivergence) <= CONVERGEDVALUE:
        converged = True
    else:
        converged = False
    prevavdivergence = avdivergence
    

