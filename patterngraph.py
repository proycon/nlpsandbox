#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import types
import traceback
import os
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
        
    def splitpairs(self):
        """Yield pairs of subngrams that follow eachother: for A B C D: A, B C D ;  A B, C D  ; A B C , D   """
        for i in range(1,len(self)):
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
                begin = i + 1
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

        #self.rel_skipgramsub = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]
        #self.rel_skipgramsuper = {} #Relations: skipgram -> [ngram]         Ex: A * B -> [A, B]

        self.rel_skipcontent = {} #Relations: skipgram -> [skipgram]       Ex: A * C -> [B]
        self.rel_inskipcontent = {} #Relations: skipgram -> [skipgram]       Ex: B -> [A * C]

        self.rel_instances = {} #Relations: skipgram -> [anygram]             Ex: A * * D -> [A * C D, A B * D, A B C D]
        self.rel_patterns = {}  #Relations: skipgram -> [anypgram]          Ex: A B * D -> [A * * D]

        self.rel_wider  ={}  #Relations: skipgram -> [skipgram]          Ex: A * D -> [A * * D, A * * * D]
        self.rel_narrower  ={}  #Relations: skipgram -> [skipgram]          Ex: A * * D -> [A * D]


        self.rel_follows = {} #Relations: anygram -> [anygram]             Ex :  D E F -> [A B C]
        self.rel_preceeds = {} #Relations: anygram -> [anygram]            Ex :  A B C -> [D E F]


        print >>sys.stderr, "Loading skipgrams"        
        self.freqlist, self.totalskipgramtokens,self.totalskipgramtypes = self.loadskipgrams(skipgramfile, self.freqlist)
        self.totaltokens = self.totalngramtokens + self.totalskipgramtokens        
        print >>sys.stderr, "\t" + str(self.totalskipgramtypes) + " types, " +  str(self.totalskipgramtokens) + " tokens"


        print >>sys.stderr, "Computing parenthood/compositionality"

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

        print >>sys.stderr, "\tgrams with children: " + str(len(self.rel_children))                        
        print >>sys.stderr, "\tgrams with parents: " + str(len(self.rel_parents))                        
                            

        print >>sys.stderr, "Computing skipgram<->ngram relations"

        for n in range(2,self.max_n+1):
            for skipgram in self.freqlist.keys():
                if isinstance(skipgram, SkipGram):
                    #for subngram in skipgram.parts():
                    #    if subngram in self.freqlist:
                    #        try:
                    #            self.rel_skipgramsub[skipgram].add(subngram)
                    #        except KeyError:
                    #            self.rel_skipgramsub[skipgram] = set( (subngram,) )
                    #            
                    #        try:
                    #            self.rel_skipgramsuper[subngram].add(skipgram)
                    #        except KeyError:
                    #            self.rel_skipgramsuper[subngram] = set( (skipgram,) )

                                                
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

            

        #print >>sys.stderr, "\tskipgrams that contain known n-grams in their component: " + str(len(self.rel_skipgramsuper))        
        #print >>sys.stderr, "\tn-grams that occur as component of a skipgram: " + str(len(self.rel_skipgramsuper))                        
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
                    elif not gram2 in self.rel_preceeds[gram1]:
                        self.rel_preceeds[gram1][gram2] = self.freqlist[gram]
                    else:
                        self.rel_preceeds[gram1][gram2] += self.freqlist[gram]            
            
        print >>sys.stderr, "\tgrams with a right neighbour: " + str(len(self.rel_preceeds))                        
        print >>sys.stderr, "\tgrams with a left neighbour: " + str(len(self.rel_follows))                            
            
        print >>sys.stderr, "Computing skipgram scoping relations"


        processed = {}
        l = len(self.freqlist.keys())        
        prevp = -1
        for i, skipgram in enumerate(self.freqlist.keys()):
            p = round((i / float(l)) * 100)
            if p % 5 == 0 and p != prevp:
                prevp = p
                print >>sys.stderr, '\t@' +  str(p) + '%'
            
            if isinstance(skipgram, SkipGram):
                for skipgram2 in  self.freqlist.keys():                    
                        if isinstance(skipgram2, SkipGram) and skipgram.matchmask(skipgram2):
                            
                            if len(skipgram) > len(skipgram2):
                                try:
                                    self.rel_wider[skipgram].add(skipgram2)
                                except KeyError:
                                    self.rel_wider[skipgram] = set( (skipgram2,) )                    
                                
                                try:
                                    self.rel_narrower[skipgram2].add(skipgram)
                                except KeyError:
                                    self.rel_narrower[skipgram2] = set( (skipgram,) )                    

                            
                        elif skipgram.match(skipgram2):
                            try:
                                self.rel_instances[skipgram].add(skipgram2)
                            except KeyError:
                                self.rel_instances[skipgram] = set( (skipgram2,) )                    
                            
                            try:
                                self.rel_patterns[skipgram2].add(skipgram)
                            except KeyError:
                                self.rel_patterns[skipgram2] = set( (skipgram,) )                      
                                         
                                                

        print >>sys.stderr, "\tskipgrams with a wider variant: " + str(len(self.rel_wider))                        
        print >>sys.stderr, "\tskipgrams with a narrower variant: " + str(len(self.rel_narrower))                        
        print >>sys.stderr, "\tskipgrams that have instances: " + str(len(self.rel_instances))                                            
        print >>sys.stderr, "\tgrams that are covered by a pattern: " + str(len(self.rel_patterns))                                            

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


    def nodeid(self,gram): #for graphviz
        return "n" + str(hash(gram)).replace('-','m')

    def graph(self, gram ):        
        """Return a dotgraph (graphviz) for a specific gram"""
        if not gram in self.freqlist:
            raise KeyError
        
        
        edges = []
        
        blacknodes = set()
        
        if gram in self.rel_children:
            for gram2 in self.rel_children[gram]:
                blacknodes.add(gram2)
                edges.append(self.nodeid(gram2) + " -> " + self.nodeid(gram) + ' [ color=black ];')                
        
        if gram in self.rel_parents:
            for gram2 in self.rel_parents[gram]:
                if not gram2 in blacknodes:
                    blacknodes.add(gram2)
                    edges.append(self.nodeid(gram) + " -> " + self.nodeid(gram2) + ' [ color=black ];' )
        
        
        greennodes = set()

        if gram in self.rel_preceeds:
            total = sum( ( x[1] for x in self.rel_preceeds[gram].items()) )
            for gram2, freq in self.rel_preceeds[gram].items():
                greennodes.add(gram2)
                edges.append(self.nodeid(gram) + " -> " + self.nodeid(gram2) + ' [ color=green,label="'+str(freq/float(total))+'" ];')                
        
        if gram in self.rel_follows:
            total = sum( ( x[1] for x in self.rel_follows[gram].items()) )
            for gram2, freq in self.rel_follows[gram].items():
                if not gram2 in greennodes:
                    greennodes.add(gram2)
                    edges.append(self.nodeid(gram2) + " -> " + self.nodeid(gram) + ' [ color=green,label="'+str(freq/float(total))+'" ];')                

     
                
        bluenodes = set()

        if gram in self.rel_inskipcontent:
            for gram2 in self.rel_inskipcontent[gram]: 
                bluenodes.add(gram2)
                edges.append(self.nodeid(gram) + " -> " + self.nodeid(gram2) + ' [ color=blue ];' )
                
        if gram in self.rel_skipcontent:
            for gram2 in self.rel_skipcontent[gram]: 
                if not gram2 in bluenodes:
                    bluenodes.add(gram2)
                    edges.append(self.nodeid(gram2) + " -> " + self.nodeid(gram) + ' [ color=blue ];' )                   
                    
                    
        purplenodes = set()

        if gram in self.rel_instances:
            for gram2 in self.rel_instances[gram]: 
                purplenodes.add(gram2)
                edges.append(self.nodeid(gram) + " -> " + self.nodeid(gram2) + ' [ color=purple ];' )
                
        if gram in self.rel_patterns:
            for gram2 in self.rel_patterns[gram]: 
                if not gram2 in purplenodes:
                    purplenodes.add(gram2)
                    edges.append(self.nodeid(gram2) + " -> " + self.nodeid(gram) + ' [ color=purple ];' )   
                    
                                        
                    
        nodes = blacknodes | greennodes | bluenodes | purplenodes

        #Find 2nd order relations between all found nodes
        for node1 in nodes:
            for node2 in nodes:
                if node1 in self.rel_children and node2 in self.rel_children[node1]:
                    edges.append(self.nodeid(node2) + " -> " + self.nodeid(node1) + ' [ color=black ];' )
                #if node1 in self.rel_parents and node2 in self.rel_parents[node1]:                    
                #    edges.append(self.nodeid(node1) + " -> " + self.nodeid(node2) + ' [ color=black ];' )                    
                #if node1 in self.rel_preceeds and node2 in self.rel_preceeds[node1]:
                #    total = sum( ( x[1] for x in self.rel_preceeds[node1].items()) )
                #    edges.append(self.nodeid(node1) + " -> " + self.nodeid(node2) + ' [ color=green,label="'+str(self.rel_preceeds[node1][node2]/float(total))+'" ];')                
                #if node1 in self.rel_follows and node2 in self.rel_follows[node1]:
                #    total = sum( ( x[1] for x in self.rel_follows[node1].items()) )
                #    edges.append(self.nodeid(node2) + " -> " + self.nodeid(node1) + ' [ color=green,label="'+str(self.rel_follows[node1][node2]/float(total))+'" ];')                                    
                if node1 in self.rel_instances and node2 in self.rel_instances[node1]:
                    edges.append(self.nodeid(node1) + " -> " + self.nodeid(node2) + ' [ color=purple ];' )
                #if node1 in self.rel_skipgramsub and node2 in self.rel_skipgramsub[node1]:
                #    edges.append(self.nodeid(node2) + " -> " + self.nodeid(node1) + ' [ color=purple ];' )
                    
                if node1 in self.rel_inskipcontent and node2 in self.rel_inskipcontent[node1]:
                    edges.append(self.nodeid(node1) + " -> " + self.nodeid(node2) + ' [ color=blue ];' )
                #if node1 in self.rel_skipcontent and node2 in self.rel_skipcontent[node1]:
                #    edges.append(self.nodeid(node2) + " -> " + self.nodeid(node1) + ' [ color=blue ];' )                    
                    
        dot = "digraph G {\n"
        #dot += "concentrate=true;\n"        
        if isinstance(gram, SkipGram):
            dot += self.nodeid(gram) + " [ fontsize=24, label=\""+str(gram).replace('"','&quot;') +"\\n"+ str(self.freqlist[gram])+"\",color=yellow, shape=circle,style=filled ];\n"
        else:
            dot += self.nodeid(gram) + " [ fontsize=24, label=\""+str(gram).replace('"','&quot;') +"\\n"+ str(self.freqlist[gram])+"\", color=yellow, shape=box,style=filled ];\n"
            
        for node in nodes:
            if isinstance(node, SkipGram):    
                dot += self.nodeid(node) + " [ label=\""+str(node).replace('"','&quot;') +"\\n"+ str(self.freqlist[node]) + "\",shape=circle ];\n"                
            else:
                dot += self.nodeid(node) + " [ label=\""+str(node).replace('"','&quot;') +"\\n"+ str(self.freqlist[node]) + "\",shape=box ];\n"                
        for edge in edges:
            dot += edge + '\n'
            
        dot += "}\n"
                            
        return DotGraph(dot)
        

class DotGraph():
    def __init__(self,data):
        self.data = data  
        
    def make(self,filename='/tmp/patterngraph.pdf'):
        f = open('/tmp/patterngraph.dot','w')
        f.write(self.data)
        f.close()
        os.system('dot -Tpdf /tmp/patterngraph.dot -o ' + filename)
        
        
        
                


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
    print 'g.graph(Q("Test text")))       -- Obtain the consecutive components in a skipgram'
    print 'Use variable _ for the last result'


def show(x):
    global g,_   
    PDFVIEWER = 'evince'  
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
    elif isinstance(x, DotGraph):
        x.make()
        os.system(PDFVIEWER + ' /tmp/patterngraph.pdf')
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
    

