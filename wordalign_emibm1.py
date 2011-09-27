#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

from pynlpl.textprocessors import Classer
from pynlpl.statistics import FrequencyList

import sys
sourcecorpus = sys.argv[1]
targetcorpus = sys.argv[2]


def buildclasser(file):
    freqlist = FrequencyList()
    f = open(file,'r')
    for line in f:
        freqlist.append(line.strip().split(' '))
    f.close()
    return Classer(freqlist)

print >>sys.stderr, "Building classer for source corpus"
sourceclasser = buildclasser(sourcecorpus)
print >>sys.stderr, "Building classer for target corpus"
targetclasser = buildclasser(targetcorpus)


source = open(sourcecorpus,'r')
target = open(targetcorpus,'r')
while True:
    sourcesentence = source.read()
    targetsentence = target.read()
    if not sourcesentence or not targetsentence:
        break
    sourcesentence = soureclasser.encode(sourcesentence.strip().split(' '))
    targetsentence = targetclasser.encode(targetsentence.strip().split(' '))
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
total = {}
count = {}
converged = False

while not converged:
    for sourcesentence, targetsentence in sentencepairs:
        #compute sentencetotal for normalisation 
        for wt in targetsentence:    
            stotal[wt] = sum( ( transprob[(wt,ws)] for ws in sourcesentence if (wt,ws) in transprob ) )        
            
        #collect counts
        for wt in targetsentence:
            for ws in sourcesentence:
                try:
                    value =  transprob[(wt,ws)] / float(stotal[wt])
                except KeyError:
                    pass #no problem
                try:
                    count[(wt,ws)] += value 
                except KeyError:
                    count[(wt,ws)] = value 
                try:
                    total[ws] += value 
                except KeyError:
                    total[ws] = value
            
        converged = True
        #estimate probabilities
        for wt in targetsentence:
            for ws in sourcesentence:
                try:
                    prevvalue = transprob[(wt,ws)]
                except KeyError:
                    prevvalue = 0
                value = count[(wt,ws)] / float(total[ws])
                transprob[(wt,ws)] = value
                if value != prevalue:
                    converged = False

            
    

