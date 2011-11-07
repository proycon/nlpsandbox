#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import types
import traceback
from pynlpl.statistics import Distribution


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
        l = len(self)
        for begin in range(0,len(self.data)):
            for length in range(1, len(self.data)-begin+1):
                if length < l:
                    yield NGram(self.data[begin:begin+length])
    
    def prefixes(self):
        for length in range(len(self.data), len(self.data) - 1):
            yield NGram(self.data[:length])
        
    def suffixes(self):
        for length in range(len(self.data), len(self.data) - 1):
            yield NGram(self.data[-length:])
            
    def __contains__(self, other):
        return (other in self.subngrams())
    
    def match(self, other):
        return self.data == other.data
    
    def __eq__(self, other):
        return self.data == other.data
        
    def __str__(self):
        return " ".join([ str(x) for x in self.data ])
        
    def split(self, index):
        assert index > 0 and index < len(self)
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
        if isinstance(other, Gap):
            return other.size == self.size
        else:
            return False
    

class SkipGram(NGram):
    def __init__(self, l, skipcontent=None):
        super(SkipGram,self).__init__(l)
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
        """Matches against other skipgrams if they have the same mask, regardless of gap size"""
        if len(other.data) != len(self.data):
            return False
        for w1, w2 in zip(self.data, other.data):
            if isinstance(w1, Gap) and isinstance(w2, Gap):
                #good, match
                pass
            elif w1 != w2:
                return False
        return True
        
    #def flexmatch(self, other):
    #    """Flexible match: gap size are maximum length, accepts shorter solutions"""
    #    
    #    cursor1 = 0
    #    cursor2 = 0
    #    
    #    while cursor1 < len(self.data) and cursor2 < len(self.data):
    #        if isinstance(cursor1,Gap):
    #            
    #        
    #    return True
            
            
    def match(self, other):
        if len(other) != len(self):
            return False        
        
        if isinstance(other, SkipGram):
            other = other.simpleform()
            
        for w1, w2 in zip(self.simpleform(), other):
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
                
        
            
class PatternGraph(object):        
            
    def loadngrams(self,filename):
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
        
    def loadskipgrams(self,filename, freqlist):
        max_n = 0
        totaltokens = 0
        totaltypes = 0
        f = open(filename)
        for line in f:
            fields = line.split('\t')
            skipgram = self.parseskipgram(fields[1], fields[9])        
            freqlist[skipgram] = int(fields[2])
            totaltypes += 1
            totaltokens += int(fields[2])
        f.close()    
        return freqlist, totaltokens, totaltypes


    def parseskipgram(self, skipgram_s, skipcontentdata=None):    
        if skipcontentdata:
            skipcontentdata = skipcontentdata.split('|')            
            skipcontentdata = dict(zip([ self.parseskipgram(x) for x in skipcontentdata[0::2] ], skipcontentdata[1::2]))    
        
        rawdata = skipgram_s.split(' ')
        data = []
        for x in rawdata:
            if x[:2] == '{*' and x[-2:] == '*}' and x[2:-2].isdigit():
                data.append(Gap(int(x[2:-2])))
            else:
                data.append(x)
                    
        return SkipGram(data, skipcontentdata)
        
    def __iter__(self):
        for x in self.freqlist.keys():
            yield x
        
    def __init__(self, ngramfile, skipgramfile):
        print >>sys.stderr, "Loading n-grams"

        self.freqlist, self.totalngramtokens, self.max_n = self.loadngrams(ngramfile)

        print >>sys.stderr, "\t" + str(len(self.freqlist)) + " types, " +  str(self.totalngramtokens) + " tokens"

        self.rel_children = {} #Relations: ngram -> [subngram]             Ex: A B C -> [A,B,C,A B, B C]
        self.rel_parents = {} #Relations: ngram -> [superngram]            Ex: A -> [A B C] 

        self.rel_skipgramsub = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]
        self.rel_skipgramsuper = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]

        self.rel_skipcontent = {} #Relations: skipgram -> [skipgram]       Ex: A * C -> [B]
        self.rel_inskipcontent = {} #Relations: skipgram -> [skipgram]       Ex: B -> [A * C]

        self.rel_subsumes = {} #Relations: skipgram -> [skipgram]             Ex: A * * D -> [A * C D, A B * D]
        self.rel_contained ={}  #Relations: skipgram -> [skipgram]          Ex: A B * D -> [A * * D]

        self.rel_wider  ={}  #Relations: skipgram -> [skipgram]          Ex: A * D -> [A * * D, A * * * D]
        self.rel_narrower  ={}  #Relations: skipgram -> [skipgram]          Ex: A * * D -> [A * D]


        self.rel_follows = {} #Relations: anygram -> [anygram]             Ex :  D E F -> [A B C]
        self.rel_preceeds = {} #Relations: anygram -> [anygram]            Ex :  A B C -> [D E F]


        print >>sys.stderr, "Computing parenthood on n-grams"

        for n in range(2,self.max_n+1):
            for ngram in self.freqlist.keys():
                if len(ngram) == n:
                    for subngram in ngram.subngrams():
                        if subngram in self.freqlist:
                            try:
                                self.rel_children[ngram].add(subngram)
                            except KeyError:
                                self.rel_children[ngram] = set( (subngram,) )
                            
                            try:
                                self.rel_parents[subngram].add(ngram)
                            except KeyError:
                                self.rel_parents[subngram] = set( (ngram,) )

        print >>sys.stderr, "\tn-grams with children: " + str(len(self.rel_children))                        
        print >>sys.stderr, "\tn-grams with parents: " + str(len(self.rel_parents))                        

        print >>sys.stderr, "Loading skipgrams"
                                
        self.freqlist, self.totalskipgramtokens,self.totalskipgramtypes = self.loadskipgrams(skipgramfile, self.freqlist)

        self.totaltokens = self.totalngramtokens + self.totalskipgramtokens

        print >>sys.stderr, "\t" + str(self.totalskipgramtypes) + " types, " +  str(self.totalskipgramtokens) + " tokens"

        print >>sys.stderr, "Computing skipgram<->ngram relations"

        for n in range(2,self.max_n+1):
            for skipgram in self.freqlist.keys():
                if isinstance(skipgram, SkipGram):
                    for subngram in skipgram.parts():
                        if subngram in self.freqlist:
                            try:
                                self.rel_skipgramsub[skipgram].add(subngram)
                            except KeyError:
                                self.rel_skipgramsub[skipgram] = set( (subngram,) )
                                
                            try:
                                self.rel_skipgramsuper[subngram].add(skipgram)
                            except KeyError:
                                self.rel_skipgramsuper[subngram] = set( (skipgram,) )

                                                
                    for content in skipgram.skipcontent.keys():
                        for subngram in content.parts():
                            if subngram in self.freqlist:
                                try:
                                    self.rel_skipcontent[skipgram].add(subngram)
                                except KeyError:
                                    self.rel_skipcontent[skipgram] = set( (subngram,) )
                            
                                try:
                                    self.rel_inskipcontent[subngram].add(skipgram)
                                except KeyError:
                                    self.rel_inskipcontent[subngram] = set( (skipgram,) )

            

        print >>sys.stderr, "\tskipgrams that contain known n-grams in their component: " + str(len(self.rel_skipgramsuper))        
        print >>sys.stderr, "\tn-grams that occur as component of a skipgram: " + str(len(self.rel_skipgramsuper))                        
        print >>sys.stderr, "\tskipgrams that contain known n-grams in their content: " + str(len(self.rel_skipcontent))        
        print >>sys.stderr, "\tn-grams that occur in the content of a skipgram: " + str(len(self.rel_inskipcontent))                        


            
                    
        print >>sys.stderr, "Computing order relations"    
            

        for gram in self.freqlist.keys():
            for gram1, gram2 in gram.splitpairs():
                if gram1 in self.freqlist and gram2 in self.freqlist:                                                        
                    if not gram2 in self.rel_follows:
                        self.rel_follows[gram2] = {gram1: self.freqlist[gram] }
                    elif not gram1 in self.rel_follows[gram2]:
                        self.rel_follows[gram2][gram1] = self.freqlist[gram]
                    else:
                        self.rel_follows[gram2][gram1] += self.freqlist[gram]


                    if not gram1 in self.rel_preceeds:
                        self.rel_preceeds[gram1] = {gram2: self.freqlist[gram] }
                    elif not gram1 in self.rel_preceeds[gram1]:
                        self.rel_preceeds[gram1][gram2] = self.freqlist[gram]
                    else:
                        self.rel_preceeds[gram1][gram2] += self.freqlist[gram]            
            
        print >>sys.stderr, "\tgrams with a right neighbour: " + str(len(self.rel_preceeds))                        
        print >>sys.stderr, "\tgrams with a left neighbour: " + str(len(self.rel_follows))                            
            
        print >>sys.stderr, "Computing skipgram scoping relations"


        processed = {}
        for skipgram in []: # self.freqlist.keys():
            if isinstance(skipgram, SkipGram):
                for skipgram2 in  self.freqlist.keys():                    
                    if isinstance(skipgram2, SkipGram) and not (skipgram is skipgram2) and len(skipgram) == len(skipgram2) and not (skipgram2, skipgram) in processed:                
                        processed[(  skipgram, skipgram2 )] = True
                        if skipgram.matchmask(skipgram2):
                            if len(skipgram) > len(skipgram2):
                                try:
                                    self.rel_wider[skipgram].add(skipgram2)
                                except KeyError:
                                    self.rel_wider[skipgram] = set( (skipgram2,) )                    
                                
                                try:
                                    self.rel_narrower[skipgram2].add(skipgram)
                                except KeyError:
                                    self.rel_narrower[skipgram2] = set( (skipgram,) )                    
                                
                            elif len(skipgram) < len(skipgram2):
                                try:
                                    self.rel_wider[skipgram2].add(skipgram)
                                except KeyError:
                                    self.rel_wider[skipgram2] = set( (skipgram,) )                    
                                
                                try:
                                    self.rel_narrower[skipgram].add(skipgram2)
                                except KeyError:
                                    self.rel_narrower[skipgram] = set( (skipgram2,) )                           
                                
                            
                        elif skipgram.match(skipgram2):
                            try:
                                self.rel_subsumes[skipgram].add(skipgram2)
                            except KeyError:
                                self.rel_subsumes[skipgram] = set( (skipgram2,) )                    
                            
                            try:
                                self.rel_contained[skipgram2].add(skipgram)
                            except KeyError:
                                self.rel_contained[skipgram2] = set( (skipgram,) )                      
                            
                        elif skipgram2.match(skipgram):
                            try:
                                self.rel_contained[skipgram].add(skipgram2)
                            except KeyError:
                                self.rel_contained[skipgram] = set( (skipgram2,) )                    
                            
                            try:
                                self.rel_subsumes[skipgram2].add(skipgram)
                            except KeyError:
                                self.rel_subsumes[skipgram2] = set( (skipgram,) )                      
                                                

        print >>sys.stderr, "\tskipgrams with a wider variant: " + str(len(self.rel_wider))                        
        print >>sys.stderr, "\tskipgrams with a narrower variant: " + str(len(self.rel_narrower))                        
        print >>sys.stderr, "\tskipgrams that subsume others: " + str(len(self.rel_subsumes))                                            
        print >>sys.stderr, "\tskipgrams that are subsumed by others: " + str(len(self.rel_contained))                                            

        del processed 

    def query(self, s):
        gram = self.parseskipgram(s)
        if gram in self.freqlist:
            return gram
        else:
            raise KeyError("The specified n-gram/skipgram was not found")            
            
    def count(self, gram):
        return self.freqlist[gram]
        
    def freq(self, gram):
        return self.freqlist[gram] / float(self.totaltokens)
    
    def freqngrams(self, gram):
        return self.freqlist[gram] / float(self.totalngrams)
    
    def freqskipgrams(self, gram):
        return self.freqlist[gram] / float(self.totalskipgrams)

    def next(self, gram):
        return Distribution(self.rel_preceeds[gram])

    def prev(self, gram):
        return Distribution(self.rel_follows[gram])
        
    def children(self, gram):
        return self.rel_children[gram]

    def parents(self, gram):
        return self.rel_parents[gram]

    def skipcontent(self, gram):
        return self.rel_skipcontent[gram]

    def skipcomponents(self, gram):
        return self.rel_skipcontent[gram]
        
        
    def find(self, text,n=0,partial=True,ngramsonly=False):
        results = set()           
        dynamic = False 
        if '*' in text.split(' '):
            text = text.split(' ')
            for i in range(0,len(text)):
                if text[i] == '*':
                    dynamic = True
                    text[i] == '{*9*}'                    
        subgram = self.parseskipgram(text)
        for gram in self:      
            if ngramsonly and not isinstance(gram, NGram):
                continue
            if(n == 0 or n == len(gram)):      
                if gram == subgram or subgram.match(gram): 
                    results.add( gram )
                
                if partial:
                    for subgram2 in gram.subngrams():
                        if subgram2 == subgram or subgram.match(subgram2):
                            results.add( gram )
        return results
        
        
    def findngrams(self, text,n=0):
        return self.find(text,n,partial,ngramsonly)

    def findskipgrams(self, text,n=0,partial=False):
        results = set()                
        subgram = NGram(text)
        for gram in self:                     
            if isinstance(gram, SkipGram)  and (n == 0 or n == len(gram)):
                if gram.match(subgram):
                    results.add( gram )
                if partial:
                    for subgram2 in gram.subngrams():
                        if subgram2.match(subgram):
                            results.add( gram )
        return results        


def help():
    print 'Q("Test text")                      -- Query the model for this exact ngram/skipgram'
    print 'g.find("Test text")                 -- Find all ngram/skipgrams that contain this ngram'
    print 'g.findngrams("the",3)               -- Find all trigrams containing "the"'
    print 'g.count(Q("Test text"))             -- Obtain the absolute count of the specific ngram/skipgram'
    print 'g.freq(Q("Test text"))              -- Obtain the relative frequency of the specific ngram/skipgram (normalised over all ngrams and skipgrams)'
    print 'g.freqngrams(Q("Test text"))        -- Obtain the relative frequency of the specific ngram (normalised over all ngrams)'
    print 'g.freqskipgrams(Q("Test text"))     -- Obtain the relative frequency of the specific skipgram (normalised over all skipgrams)'
    print 'g.next(Q("Test text")))             -- Obtain a distribution of constructions that follow this one' 
    print 'g.prev(Q("Test text")))             -- Obtain a distribution of constructions that preceed this one'     
    print 'g.parents(Q("Test text")))          -- Obtain all ngrams that contain the specified one'
    print 'g.children(Q("Test text")))         -- Obtain all ngrams that are contained within the specified one'
    print 'g.skipcontent(Q("The {*3*} text"))) -- Obtain the contents of a skipgram'
    print 'g.components(Q("The {*3*} text")))  -- Obtain the consecutive components in a skipgram'
    print 'Use variable _ for the last result'


def show(x):
    global g,_     
    if isinstance(x, types.GeneratorType):
        x = list(x)
    if isinstance(x, list) or isinstance(x,tuple)  or isinstance(x,set):
        if all(( y in g.freqlist for y in x )):            
            x = dict(   (y,g.freqlist[y]) for y in x )
            total = sum((y[1] for y in x.items()))
            for i, (y, z) in enumerate(sorted(x.items(), key = lambda x: -1 * x[1])):
                _ = y
                print str(i+1) + '\t' + str(y) + '\t' + str(z) + '\t' + str(z/float(total))
        else:
            for i, y in enumerate(x):
                if y in g.freqlist:
                    print str(i+1) + '\t' + str(y) + '\t' + str(g.freqlist[y])
                else:
                    print str(i+1) + '\t' + str(y) 

        print "--------------------"        
    elif isinstance(x, Distribution):
        for i, (key, value) in enumerate(x):
            print str(i+1) + '\t' + str(key) + '\t' + str(value)
        print "--------------------"
    elif isinstance(x, dict):
        for i, (key, value) in enumerate(x.items()):
            print str(i+1) + '\t' + str(key) + '\t' + str(value)
            print str(i+1) + '\t' + str(key) + '\t' + str(value)
        print "--------------------"        
    elif isinstance(x, NGram) or isinstance(x, SkipGram) and x in  g.freqlist:
        print str(x) + '\t' + str(g.freqlist[x]) 
        _ = x
    elif not (x is None):
        print str(x)



        
        
if __name__ == "__main__":
    g = PatternGraph(sys.argv[1], sys.argv[2])
    print >>sys.stderr, "Done."           
    print >>sys.stderr, "Type help() for help"
    _ = None
    Q = g.query
    while True:
        print ">>>> ",
        try: 
            c = sys.stdin.readline()
            if c.strip():
                show(eval(c.strip()))
        except KeyError:
            print "No result"
        except Exception as e:
            print "An error occurred"
            print "---------------------------------------"
            traceback.print_exc()
            print "---------------------------------------"
    



#Graphviz output
#def nodeid(gram):
#    return "n" + str(hash(gram)).replace('-','m')
    

#print "digraph G {"
#for gram in freqlist:
#    if isinstance(gram, SkipGram):
#        print nodeid(gram) + " [shape=ellipse,label=\""+str(gram).replace('"','&quot;')+"\"];"
#    else:
#        print nodeid(gram) + " [shape=box,label=\""+str(gram).replace('"','&quot;')+"\"];"
#self.rel_children[ngram].add(subngram)

#for ngram, parents in self.rel_parents.items():
#    for ngram2 in parents:
#        print nodeid(ngram) + " -> " + nodeid(ngram2) + ";"

#print "}"
