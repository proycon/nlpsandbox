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
            buffer.append( word,pos,lemma)
        
    cursor = 0
    postags = []
    lemmas = []    
    for word in words:
        found = False
        for i, (bufword,pos,lemma) in enumerate(buffer[cursor:]):
            if word == bufword:
                found = True
                cursor = i+1
                postags.append(pos)
                lemmas.append(lemma)
                break
        if not found:            
            postags.append('?')
            lemmas.append(word)
            
    buffer = buffer[cursor:]            
                
             
            
        
        
        
            
    
    
ref.close()     
    
ttf.close()    
