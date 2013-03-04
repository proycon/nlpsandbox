#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs

try:
    referencefile = sys.argv[1]
    treetagfile = sys.argv[2]
except:
    print >>sys.stderr, "Parameters: referencefile treetagfile"
    sys.exit(2)

ttf = codecs.open(treetagfile,'r','utf-8')

buffer = []

ref = codecs.open(referencefile,'r','utf-8')
for line in ref:
    words = line.strip().split(' ')
    
    if len(buffer) < len(words) + 10:
        for i in range(0,len(words) + 10):
            try:
                bufline = ttf.next()
            except StopIteration:
                break
            word,pos,lemma = bufline.strip().split('\t')
            buffer.append( (word,lemma,pos) )
        
    cursor = 0
    postags = []
    lemmas = []    
    
    alignment = {}
    for i, word in enumerate(words):
        found = False
        for j, (bufword,lemma,pos) in enumerate(buffer[cursor:]):
            if word == bufword:
                found = True
                if not i in alignment:
                    alignment[i] = []
                alignment[i].append(j)

    #resolve multiple alignments to the one closest to neighbours
    for source, targets in alignment.items():
        if len(targets) >= 1:
            mindistance = 999
            best = -1
            newtargets = []
            for target in targets:
                if source-1 in alignment and len(alignment[source-1]) == 1:
                    distance = target - alignment[source-1][0]
                    if distance > 0: #only if order is right
                        if distance < mindistance:
                            best = target
                            mindistance = distance                        
                if source+1 in alignment and len(alignment[source+1]) == 1:
                    distance = alignment[source+1][0] - target
                    if distance > 0: #only if order is right
                        if distance < mindistance:
                            best = target
                            mindistance = distance                    
            
            if best != -1:
                alignment[source] = [best]
            else:
                alignment[source] = [min(targets)]
    
            
    if not alignment:
        print >>sys.stderr, "No alignments found!"
        print >>sys.stderr, "Input:", repr(words)
        print >>sys.stderr, "Buffer:", repr(buffer)
        
 
    for i, word in enumerate(words):
        if i != 0: print " ",
        if i in alignment:
            s = word + "|" + buffer[alignment[i][0]][1] + "|" +  buffer[alignment[i][0]][2]
        else:
            s = word + "|" + word + "|?"
        print s.encode('utf-8'),
    print

   
 
    cutoff = max(alignment[x][0] for x in alignment) + 1
    buffer = buffer[cutoff:]  

        
        
            
    
    
ref.close()     
    
ttf.close()    
