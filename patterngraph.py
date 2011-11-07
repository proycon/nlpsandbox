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
            
    def __getitem__(self,i):
        return self.data[i]
        
    def __getslice__(self,b,e):
        return self.data[b:e]

    def subngrams(self):
        """Yield all sub-ngrams"""
        for begin in range(0,len(self.data)):
            for length in range(len(self.data)-begin, len(self.data)):
                yield NGram(self.data[begin:begin+length])
    
    def prefixes(self):
        for length in range(len(self.data), len(self.data) - 1):
            yield NGram(self.data[:length])
        
    def suffixes(self):
        for length in range(len(self.data), len(self.data) - 1):
            yield NGram(self.data[-length:])
            
    def __contains__(self, other):
        return (other in self.subngrams())
    
    def __eq__(self, other):
        return self.data == other.data
        
    def __str__(self):
        return " ".join([ str(x) for x in self.data ])
        
    def split(self, index):
        return ( NGram(self.data[:index]), NGram(self.data[index:]) )        
        
    def splitpairs(self, leftmargin = 1, rightmargin = 1):
        """Yield pairs of subngrams that follow eachother: for A B C D: A, B C D ;  A B, C D  ; A B C , D   """
        for i in range(leftmargin,len(self) - rightmargin):
            yield self.split(i)
        
        


class Gap(object):
    def __init__(self,size):
        self.size = size
        
    def __len__(self):
        return self.size;
        
    def __str__(self):
        return "{*" + str(self.size) + "*}"
    
    def __hash__(self):
        return hash(str(self))  
        
    def __eq__(self, other):
        return other.size == self.size
    

class SkipGram(NGram):
    def __init__(self, l, skipcontent=None):
        super(NGram,self).__init__(l)
        self.skipcontent = skipcontent
    
    def __len__(self):        
        l = 0
        for x in self.data:
            if isinstance(x, Gap):
                l += len(x)
            else:
                l += 1
        return l

    def skips(self):
        """Return number of skips"""
        c = 0
        for x in self.data:
            if isinstance(x, Gap):
                c += 1
        return c

    def parts(self):
        """Return the consecutive ngrams that make up the skipgram"""
        begin = 0
        length = 0
        for i, x in enumerate(self.data):
            if isinstance(x, Gap):
                if length > 0:
                    yield NGram(self.data[begin:begin+length])
                length = 0
            else:
                length += 1
        if length > 0:
            yield NGram(self.data[begin:begin+length])
            
    def matchmask(self, other):
        if len(other.data) != len(self.data):
            return False
        for w1, w2 in zip(self.data, other.data):
            if isinstance(w1, Gap) and isinstance(w2, Gap):
                #good, match
                pass
            elif w1 != w2:
                return False
        return True

            
            
    def match(self, other):
        if len(other) != len(self):
            return False
        
        for w1, w2 in zip(self.simpleform(), other.simpleform()):
            if w1 is None:
                #good, match                
                pass
            elif w1 != w2:
                return False
        return True
                
    def simpleform(self):
        """Replace gap with None elements"""
        newdata = []
        for x in self.data:
            if isinstance(x, Gap):
                newdata +=  [None] * len(x)
            else:
                newdata.append(x)        
        return tuple(newdata)
                
        
            
        

            

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
    
def loadskipgrams(filename, freqlist):
    max_n = 0
    f = open(filename)
    for line in f:
        fields = line.split('\t')
        skipgram = parseskipgram(fields[1], fields[9])        
        freqlist[skipgram] = int(fields[2])
        totaltokens += int(fields[2])
    f.close()    
    return freqlist, totaltokens


def parseskipgram(skipgram_s, skipcontentdata=None):    
    if skipcontentdata:
        skipcontentdata = skipcontentdata.split('|')            
        skipcontentdata = dict(zip([ parseskipgram(x) for x in skipcontentdata[0::2] ], skipcontentdata[1::2]))    
    
    rawdata = skipgram_s.split(' ')
    data = []
    for x in rawdata:
        if x[:2] == '{*' and x[-2:] == '*}' and x[2:-2].isdigit():
            data.append(Gap(int(x[2:-2])))
        else:
            data.append(x)
                
    return SkipGram(data, skipcontentdata)
    

print >>sys.stderr, "Loading n-grams"

freqlist, totalngramtokens, max_n = loadngrams(sys.argv[1])

print >>sys.stderr, "\t" + len(freqlist) + " types, " +  str(totalngramtokens) + " tokens"

rel_children = {} #Relations: ngram -> [subngram]             Ex: A B C -> [A,B,C,A B, B C]
rel_parents = {} #Relations: ngram -> [superngram]            Ex: A -> [A B C] 

rel_skipgramsub = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]
rel_skipgramsuper = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]

rel_skipcontent = {} #Relations: skipgram -> [skipgram]       Ex: A * C -> [B]
rel_inskipcontent = {} #Relations: skipgram -> [skipgram]       Ex: B -> [A * C]

rel_supersedes = {} #Relations: skipgram -> [skipgram]             Ex: A * * D -> [A * C D, A B * D]
rel_contained ={}  #Relations: skipgram -> [skipgram]          Ex: A B * D -> [A * * D]

rel_wider  ={}  #Relations: skipgram -> [skipgram]          Ex: A * D -> [A * * D, A * * * D]
rel_narrower  ={}  #Relations: skipgram -> [skipgram]          Ex: A * * D -> [A * D]


rel_follows = {} #Relations: anygram -> [anygram]             Ex :  D E F -> [A B C]
rel_preceeds = {} #Relations: anygram -> [anygram]            Ex :  A B C -> [D E F]


print >>sys.stderr, "Computing parenthood on n-grams"

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
                        

print >>sys.stderr, "Loading skipgrams"
                        
freqlist, totalskipgramtokens = loadskipgrams(sys.argv[2])

totaltokens = totalngramtokens + totalskipgramtokens

print >>sys.stderr, "Computing skipgram<->ngram relations"

for n in range(2,max_n+1):
    for skipgram in freqlist.keys():
        if isinstance(skipgram, SkipGram):
            for subngram in skipgram.parts():
                if subngram in freqlist:
                    try:
                        rel_skipgramsub[skipgram].add(subngram)
                    except KeyError:
                        rel_skipgramsub[skipgram] = set( (subngram,) )
                        
                    try:
                        rel_skipgramsuper[subngram].add(skipgram)
                    except KeyError:
                        rel_skipgramsuper[subngram] = set( (skipgram,) )

                                        
            for content in skipgram.skipcontent.keys():
                for subngram in content.parts():
                    if subngram in freqlist:
                        try:
                            rel_skipcontent[skipgram].add(subngram)
                        except KeyError:
                            rel_skipcontent[skipgram] = set( (subngram,) )
                    
                        try:
                            rel_inskipcontent[subngram].add(skipgram)
                        except KeyError:
                            rel_inskipcontent[subngram] = set( (skipgram,) )
    
            
print >>sys.stderr, "Computing order relations"    
    

for gram in freqlist.keys():
    for gram1, gram2 in gram.splitpairs():
        if gram1 in freqlist and gram2 in freqlist:
            try:
                rel_follows[gram2][gram1] += freqlist[gram]
            except KeyError:
                rel_follows[gram2] = {gram1: freqlist[gram] }

            try:
                rel_preceeds[gram1][gram2] += freqlist[gram]
            except KeyError:
                rel_preceeds[gram1] = {gram2: freqlist[gram] }
    
    
print >>sys.stderr, "Computing skipgram scoping relations"


processed = {}
for skipgram in freqlist.keys():
    if isinstance(skipgram, SkipGram):
        for skipgram2 in freqlist.keys():                    
            if isinstance(skipgram2, SkipGram) and not (skipgram is skipgram2) and len(skipgram) == len(skipgram2) and not (skipgram2, skipgram) in processed:                
                processed[(  skipgram, skipgram2 )] = True
                if skipgram.matchmask(skipgram2):
                    if len(skipgram) > len(skipgram2):
                        try:
                            rel_wider[skipgram].add(skipgram2)
                        except KeyError:
                            rel_wider[skipgram] = set( (skipgram2,) )                    
                        
                        try:
                            rel_narrower[skipgram2].add(skipgram)
                        except KeyError:
                            rel_narrower[skipgram2] = set( (skipgram,) )                    
                        
                    elif len(skipgram) < len(skipgrams2):
                        try:
                            rel_wider[skipgram2].add(skipgram)
                        except KeyError:
                            rel_wider[skipgram2] = set( (skipgram,) )                    
                        
                        try:
                            rel_narrower[skipgram].add(skipgram2)
                        except KeyError:
                            rel_narrower[skipgram] = set( (skipgram2,) )                           
                        
                    
                elif skipgram.match(skipgram2):
                    try:
                        rel_subsumes[skipgram].add(skipgram2)
                    except KeyError:
                        rel_subsumes[skipgram] = set( (skipgram2,) )                    
                    
                    try:
                        rel_contained[skipgram2].add(skipgram)
                    except KeyError:
                        rel_contained[skipgram2] = set( (skipgram,) )                      
                    
                elif skipgram2.match(skipgram):
                    try:
                        rel_contained[skipgram].add(skipgram2)
                    except KeyError:
                        rel_contained[skipgram] = set( (skipgram2,) )                    
                    
                    try:
                        rel_subsumes[skipgram2].add(skipgram)
                    except KeyError:
                        rel_subsumes[skipgram2] = set( (skipgram,) )                      
                                        
                

del processed 



