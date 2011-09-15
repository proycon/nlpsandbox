#!/usr/bin/python
# PBMBMT: PHRASE-BASED MEMORY-BASED MACHINE TRANSLATOR
# by Maarten van Gompel (proycon)
#   proycon AT anaproy DOT NL
#   http://proylt.anaproy.nl
# Licensed under the GNU Public License v3
# ---------------------------
# Extracts common phrases (n-grams and simple skipgrams) from one or more corpora

import sys
import codecs
from pynlpl.statistics import FrequencyList, Distribution
from pynlpl.textprocessors import Windower, crude_tokenizer
from networkx import DiGraph, write_gpickle

import getopt
import itertools
import math

def usage():
    print >> sys.stderr, "Extract a phrase list (common n-grams) from a tokenised plain text corpus"
    print >> sys.stderr, "Syntax:  pbmbmt-make-phraselist.py"
    print >> sys.stderr, "Options:"
    print >> sys.stderr, "-f <corpus-file>                 - File name of the TOKENISED plain text corpus file to process"
    print >> sys.stderr, "-t <minimal occurence threshold> - Value indicating the minimal occurence threshold for a n-gram, will be pruned otherwise (default: 2)"
    print >> sys.stderr, "-T <minimal occurence threshold> - Value indicating the minimal occurence threshold for a skip-gram, will be pruned otherwise (default: 2)"
    print >> sys.stderr, "-l <minimal length>              - Minimal length of n-grams (default: 2)"    
    print >> sys.stderr, "-L <maximum length>              - Maximum length of n-grams (default: 6)"    
    print >> sys.stderr, "-s                               - compute simple skip-n-grams (output in separate file)"    
    print >> sys.stderr, "-C                               - use classer (saves memory and speeds up computation, but only when dealing with large data sets, outputs an extra .cls file)"
    print >> sys.stderr, "-c                               - compute compositional data (memory intensive!)" 
    print >> sys.stderr, "-I                               - maintain and output index file (separate file, memory intensive!)"    
    print >> sys.stderr, "-S                               - Output all possible skips in .skipgram file (no significant cpu/memory cost)"    
    print >> sys.stderr, "-o <output prefix>               - path + filename, .phraselist extension will be added automatically. If not set, will be derived from input file."    
    print >> sys.stderr, "-p                               - Input is not tokenised, apply crude built-in tokeniser."
    print >> sys.stderr, "-e <encoding>                    - Encoding of input file (default: utf-8, note that output is always utf-8 regardless)"    
    


corpusfile = outputprefix = None
MINOCCURRENCES = MINSKIPOCCURRENCES = 2
MINLENGTH = 2
MAXLENGTH = 6
DOSKIPGRAMS = False
DOSKIPOUTPUT = False
DOCOMPOSITIONALITY = False
DOTOKENIZE = False
DOINDEX = False
DOCLASSER = False
ENCODING = 'utf-8'

try:
    opts, args = getopt.getopt(sys.argv[1:], "f:ht:T:l:L:sco:e:pIC")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-f':
        corpusfile = a
    elif o == '-t':
        MINOCCURRENCES = int(a)
    elif o == '-T':
        MINSKIPOCCURRENCES = int(a)    
    elif o == '-l':
        MINLENGTH = int(a)   
    elif o == '-L':
        MAXLENGTH = int(a)   
    elif o == '-h':
        usage()
        sys.exit(0)
    elif o == '-o':
        outputprefix = a
    elif o == '-s':
        DOSKIPGRAMS = True
    elif o == '-c':
        DOCOMPOSITIONALITY = True    
    elif o == '-C':
        DOCLASSER = True
    elif o == '-e':
        ENCODING = a
    elif o == '-I':
        DOINDEX = True
    elif o == '-S':
        DOSKIPOUTPUT = True
    else:
        raise Exception("No such option: " + o)

if not corpusfile:
	usage()
	sys.exit(2)

if not outputprefix:
    outputprefix = corpusfile

if DOCLASSER:
    print >> sys.stderr, "Counting unigrams (for classer) ..."
    freqlist = FrequencyList
    f = codecs.open(corpusfile,'r',ENCODING)
    for i, line in enumerate(f):            
        if (i % 10000 == 0): 
            print >>sys.stderr, "\tLine " + str(i+1) + " - (classer construction)"
        if DOTOKENIZE: 
            line = crude_tokenizer(line.strip())
        freqlist.append(line)
    f.close()
    
    print >> sys.stderr, "Building classer ..."
    classer = Classer(freqlist)
    classer.save(outputprefix + '.cls')
    

f = codecs.open(corpusfile,'r',ENCODING)
if DOCLASSER and MINLENGTH <= 1:
    freqlist = {1: freqlist}
else:
    freqlist = {}
if DOINDEX: index = {}
if DOSKIPGRAMS: simpleskipgrams = {}
dist = {}
iteration = 0
for n in xrange(MINLENGTH,MAXLENGTH+1):
    freqlist[n] = FrequencyList(None,True,False) #tokens=None, casesensitive=True, dovalidation=False
    if DOSKIPGRAMS: 
        simpleskipgrams[n] = {}
        skips = {}
    print >> sys.stderr, "Counting "+str(n)+"-grams ..."
    f.seek(0)
    iteration += 1
    for i, line in enumerate(f):            
        if (i % 10000 == 0): 
            if iteration == 1:
                print >>sys.stderr, "\tLine " + str(i+1) + " - (" + str(n) + "-grams)"
            else:
                print >>sys.stderr, "\tLine " + str(i+1) + " of " + str(linecount) + " - " + str( round(((i+1) / float(linecount)) * 100)) + "% " + " (" + str(n) + "-grams)"  
        if iteration == 1: linecount = i+1
        if DOTOKENIZE: 
            line = crude_tokenizer(line.strip())
        else:
            line = [ x for x in line.strip().split(' ') if x ]
        for ngram in Windower(line,n):
            if DOCLASSER: ngram = tuple(classer.encode(ngram))
            if n - 1 in freqlist:
                count = (ngram[1:] in freqlist[n-1] and ngram[:-1] in freqlist[n-1])
            else:
                count = True
            if count:
                freqlist[n].count(ngram)
                if DOSKIPGRAMS and n >= 3 and ngram[0] != '<begin>' and ngram[-1] != '<end>':
                    skipgram =  ( (ngram[0],) , (ngram[-1],) )
                    body = tuple(ngram[1:-1])
                    if not skipgram in simpleskipgrams[n]: #using None key for overall count to save computation time later
                        simpleskipgrams[n][skipgram] = {None: 1}
                    else:
                        simpleskipgrams[n][skipgram][None] += 1
                    if body in simpleskipgrams[n][skipgram]:
                        simpleskipgrams[n][skipgram][body] += 1
                    else:
                        simpleskipgrams[n][skipgram][body] = 1
                    
                    #simpleskipgrams[n].count( skipgram )                     
                    #try:
                    #    skips[skipgram].append( ngram[1:-1] )
                    #except:
                    #    skips[skipgram] = [ ngram[1:-1] ]
                            
    if MINOCCURRENCES > 1:
        print >>sys.stderr, "Pruning " + str(n) + "-grams..."
        for ngram, count in freqlist[n]:
            if count < MINOCCURRENCES:
                del freqlist[n][ngram]        
                if DOSKIPGRAMS:
                    skipgram = ( (ngram[0],) , (ngram[-1],) )
                    if skipgram in simpleskipgrams[n] and simpleskipgrams[n][skipgram][None] <= count:
                        #note: if skip-grams are not found on the same n-level, they are pruned because of this early-pruning
                        del simpleskipgrams[n][skipgram]
        
                    
    
    if DOSKIPGRAMS:
        l = len(simpleskipgrams[n])
        print >>sys.stderr, "Pruning skip-" + str(n) + "-grams... (" +str(l)+")"
        for i, (skipgram, data) in enumerate(simpleskipgrams[n].items()):
            if i % 1000 == 0:  print >>sys.stderr, '\t\t@' + str(i)
            if len(data) - 1 == 1: #Minus the meta None/count entry
                del simpleskipgrams[n][skipgram]
        print >>sys.stderr, "\t" +str(len(simpleskipgrams[n])) + " left after pruning"

        print >>sys.stderr, "Expanding skip-" + str(n) + "-grams..."
        #Expand skip-grams
        expansionsize = 0
        if n > 3:
            cacheitems = list(simpleskipgrams[n].items())
            for p, (skipgram, data) in enumerate(cacheitems):
                if p % 1000 == 0:  print >>sys.stderr, '\t\t@' + str(p)
                for skip, skipcount in data.items():            
                    if skip:
                        for skip2, skipcount2 in simpleskipgrams[n][skipgram].items():                        
                            if skip != skip2 and skip2:
                                overlapmask = [ w1 if w1 == w2 else None for w1,w2 in zip(skip,skip2) ]
                                left = []
                                right = []
                                position = 0
                                consecutive = True
                                gap = 0
                                prev = None
                                gapbegin = 0
                                gapsize = 1
                                for i, w in enumerate(overlapmask):
                                    if w:
                                        if position == 0:
                                            left.append(w)
                                        elif position == 1:
                                            right.append(w)                                    
                                    else:
                                        if position == 0:
                                            gapbegin = i
                                            position = 1
                                        elif position == 1 and prev:
                                            #multiple gaps
                                            consecutive = False    
                                            break
                                        else:
                                            gapsize += 1
                                    prev = w
                                    
                                if not consecutive: continue
                                
                                #content of new gap
                                newskip = skip2[gapbegin:gapbegin+gapsize]
                        
                                newskipgram = ( skipgram[0] + tuple(left), tuple(right) + skipgram[-1] )
                                try:
                                    simpleskipgrams[n][newskipgram][None] += 1
                                except:
                                    simpleskipgrams[n][newskipgram] = {None: 1}
                                    expansionsize += 1
                                try:
                                    simpleskipgrams[n][newskipgram][newskip] += 1
                                except:
                                    simpleskipgrams[n][newskipgram][newskip] = 1

                                
        
        print >>sys.stderr, "Found " + str(len(freqlist[n])) + " " + str(n) + "-grams and " + str(len(simpleskipgrams[n])) + " skip-" + str(n) + "-grams, of which "+str(expansionsize) + " from expansion step)"             
    else:
        print >>sys.stderr, "Found " + str(len(freqlist[n])) +  " " + str(n) + "-grams"         
    
if DOCOMPOSITIONALITY:
    compgraph = DiGraph()
    for n in freqlist:
        print >>sys.stderr, "Computing compositionality graph (processing " +str(n) + "-grams)"
        l = len(freqlist[n])
        for i, (ngram, count) in enumerate(freqlist[n]):
            if (i % 10000 == 0): 
                print >>sys.stderr, '\t' + str(float(round((i/float(l))*100,2))) + '%'
            for n2 in range(MINLENGTH,n):
                for subngram in Windower(ngram,n2):
                    if subngram in freqlist[n2]:
                        compgraph.add_edge(subngram, ngram)        

    print >>sys.stderr, "Writing compositionality graph to file"

    write_gpickle(compgraph, outputprefix + '.compgraph')

totalcount = 0
for n in freqlist:
    totalcount += sum([ f for f in freqlist[n].values() ])
            
print >>sys.stderr, "Writing n-grams to file"

f = codecs.open(outputprefix + '.phraselist', 'w','utf-8')
f.write('#N\tN-GRAM\tOCCURRENCE-COUNT\tNORMALISED-IN-NGRAM-CLASS\tNORMALISED-OVER-ALL\tSUBCOUNT\tSUPERCOUNT\n')
for n in freqlist:
    for ngram, count in freqlist[n]:
        if DOCLASSER:
            ngram_s = " ".join(classer.decodeseq(ngram))        
        else:
            ngram_s = " ".join(ngram)        
        if DOCOMPOSITIONALITY:
            subcount = str(len(compgraph.out_edges(ngram)))
            supercount = str(len(compgraph.in_edges(ngram)))
        else:
            subcount = '-'
            supercount = '-'
        f.write(str(len(ngram)) + '\t' + ngram_s + '\t' + str(count) + '\t' + str(freqlist[n].p(ngram)) + '\t' + str(freqlist[n][ngram] / float(totalcount)) + '\t' + subcount + '\t' + supercount + '\n')

f.close()
    
if DOSKIPGRAMS:
    print >>sys.stderr, "Writing skip-n-grams to file"
    totalskipgramcount = 0
    for n in simpleskipgrams:
        totalskipgramcount += sum( ( f[None] for f in simpleskipgrams[n].values()  ) )
    
    f = codecs.open(outputprefix + '.skipgrams', 'w','utf-8')    
    f.write('#N\tSKIP-N-GRAM\tOCCURRENCE-COUNT\tNORMALISED-OVER-ALL\tSKIPCONTENT-TYPES\tSKIPCONTENT-TOKENS\tSKIPCONTENT-ENTROPY\tSKIPS\n')
    for n in simpleskipgrams:
        for skipgram, data in simpleskipgrams[n].items():
            count = data[None]
            if DOCLASSER:
                skipgram_s = " ".join(classer.decodeseq(skipgram[0])) + " * " + " ".join(classer.decodeseq(skipgram[-1]))
            else:
                skipgram_s = " ".join(skipgram[0]) + " * " + " ".join(skipgram[-1])
            totalskipcount = 0
            skips = 0
            entropy = 0
            if DOSKIPOUTPUT:
                skipoutput = ''
            else:
                skipoutput = '-'
            for skip, skipcount in data.items():
                if skip:
                    skips += 1
                    totalskipcount += skipcount                                              
                    entropy += skipcount * -math.log(skipcount)                                                          
                    if DOSKIPOUTPUT:
                        if DOCLASSER:
                            skipoutput += '_'.join(classer.decodeseq(skip)) + ' '
                        else:
                            skipoutput += '_'.join(skip) + ' '
                        skipoutput = skipoutput.rstrip()
            f.write(str(n) + '\t' + skipgram_s + '\t' + str(count) + '\t' + str(count / float(totalskipgramcount)) + '\t' + str(skips) + '\t' + str(totalskipcount) + '\t' + str(entropy) + '\t' + skipoutput + '\n')
            

    f.close()


