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
    count = {}
    
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
            
        #collect counts
        for wt in targetsentence:
            for ws in sourcesentence:
                try:
                    value =  transprob[(wt,ws)] / float(stotal[wt])
                except KeyError:
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
                    prevvalue = transprob[(wt,ws)]
                except KeyError:
                    prevvalue = 0
                try:
                    value = count[(wt,ws)] / float(total[ws])
                    transprob[(wt,ws)] = value
                except KeyError:
                    value = 0              
                divergence = abs(value - prevvalue)
                totaldivergence += divergence
                c += 1
    
    print transprob
    
    avdivergence = totaldivergence / float(c)
    print "\tTotal average divergence: " + str(avdivergence)
    if i >= MAXROUNDS or abs(avdivergence - prevavdivergence) <= CONVERGEDVALUE:
        converged = True
    else:
        converged = False
    prevavdivergence = avdivergence
    

