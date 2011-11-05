#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys


class NGram(object):
    def __init__(self, l):
        if isinstance(l, str) or isinstance(l, unicode):
            self.data = tuple(l.split(' '))
        elif isinstance(l, tuple):
            self.data = l
        else:
            self.data = tuple(l)
    
    def __len__(self):
        return len(self.data)
        
    def __hash__(self):
        return hash(self.data)
        
    def __iter__(self):
        for x in self.data:
            yield x

    def subngrams(self):
        """Yield all sub-ngrams"""
        for begin in range(0,len(self.data)):
            for length in range(len(self.data)-begin, len(self.data)):
                yield NGram(self.data[begin:begin+length])
    
    def __eq__(self, other):
        return self.data == other.data


def loadngrams(filename):
    freqlist = {}
    totaltokens = 0
    max_n = 0
    f = open(filename)
    for line in f:
        fields = line.split('\t')
        ngram = NGram(fields[1])
        freqlist[ngram] = int(fields[2])
        totaltokens += int(fields[2])
        if len(ngram) > max_n:
            max_n = len(ngram)        
    f.close()
    return freqlist, totaltokens, max_n



freqlist, totaltokens, max_n = loadngrams(sys.argv[1])

rel_children = {} #Relations: ngram -> [subngram]
rel_parents = {} #Relations: ngram -> [superngram]



rel_usedin = {} #Relations: ngram -> [ngram]


for n in range(2,max_n+1):
    for ngram in freqlist.keys():
        if len(ngram) == n:
            for subngram in ngram.subngrams():
                if subngram in freqlist:
                    try:
                        rel_children[ngram].add(subngram)
                    except KeyError:
                        rel_children[ngram] = set( (subngram,) )
                    
                    try:
                        rel_parents[subngram].add(ngram)
                    except KeyError:
                        rel_parents[subngram] = set( (ngram,) )
                        


            
            
            
            
    
    
    
    
    

