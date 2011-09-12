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

def usage():
    print >> sys.stderr, "Extract a phrase list (common n-grams) from a tokenised plain text corpus"
    print >> sys.stderr, "Syntax:  pbmbmt-make-phraselist.py"
    print >> sys.stderr, "Options:"
    print >> sys.stderr, "-f <corpus-file>                 - File name of the TOKENISED plain text corpus file to process"
    print >> sys.stderr, "-t <minimal occurence threshold> - Value indicating the minimal occurence threshold for a n-gram, will be pruned otherwise (default: 2)"
    print >> sys.stderr, "-T <minimal occurence threshold> - Value indicating the minimal occurence threshold for a skip-gram, will be pruned otherwise (default: 2)"
    print >> sys.stderr, "-l <minimal length>              - Minimal length of n-grams (default: 2)"    
    print >> sys.stderr, "-L <maximum length>              - Maximum length of n-grams (default: 6)"    
    print >> sys.stderr, "-s                               - compute simple skipgrams (output in separate file)"    
    print >> sys.stderr, "-c                               - compute compositional data"    
    print >> sys.stderr, "-i                               - output index file (seperate file)"    
    print >> sys.stderr, "-o <output prefix>               - path + filename, .phraselist extension will be added automatically. If not set, will be derived from input file."    
    print >> sys.stderr, "-p                               - Input is not tokenised, apply crude built-in tokeniser."
    print >> sys.stderr, "-e <encoding>                    - Encoding of input file (default: utf-8, note that output is always utf-8 regardless)"    
    


corpusfile = outputprefix = None
MINOCCURRENCES = MINSKIPOCCURRENCES = 2
MINLENGTH = 2
MAXLENGTH = 6
DOSKIPGRAMS = False
DOCOMPOSITIONALITY = False
DOTOKENIZE = False
DOINDEX = False
ENCODING = 'utf-8'

try:
    opts, args = getopt.getopt(sys.argv[1:], "f:ht:T:l:L:sco:e:pi")
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
    elif o == '-e':
        ENCODING = a
    elif o == '-i':
        DOINDEX = True
    else:
        raise Exception("No such option: " + o)

if not corpusfile:
	usage()
	sys.exit(2)

if not outputprefix:
    outputprefix = corpusfile

f = codecs.open(corpusfile,'r',ENCODING)
freqlist = {}
if DOSKIPGRAMS: simpleskipgrams = {} 
if DOINDEX: index = {}
dist = {}
iteration = 0
for n in xrange(MINLENGTH,MAXLENGTH+1):
    freqlist[n] = FrequencyList()
    if DOSKIPGRAMS: simpleskipgrams[n] = FrequencyList()
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
            if n - 1 in freqlist:
                count = (ngram[1:] in freqlist[n-1] and ngram[:-1] in freqlist[n-1])
            else:
                count = True
            if count:
                freqlist[n].count(ngram)
                if DOSKIPGRAMS and n >= 3:
                    if ngram[0] != '<begin>' and ngram[1] != '<begin>' and ngram[0] != '<end>' and ngram[1] != '<end>':
                        simpleskipgrams[n].count( (ngram[0], ngram[-1]) ) 
                    
                    
            
    if MINOCCURRENCES > 1:
        print >>sys.stderr, "Pruning " + str(n) + "-grams..."
        for ngram, count in freqlist[n]:
            if count < MINOCCURRENCES:
                del freqlist[n][ngram]        
                if DOSKIPGRAMS and (ngram[0], ngram[-1]) in simpleskipgrams[n] and simpleskipgrams[n][(ngram[0], ngram[-1])] <= count:
                    #note: if skip-grams are not found on the same n-level, they are pruned because of this early-pruning
                    del simpleskipgrams[n][(ngram[0], ngram[-1])]
    
    if DOSKIPGRAMS:
        print >>sys.stderr, "Found " + str(len(freqlist[n])) + " " + str(n) + "-grams and " + str(len(simpleskipgrams[n])) + " simple skip-" + str(n-2) + "-grams"     
    else:
        print >>sys.stderr, "Found " + str(len(freqlist[n])) +  " + str(n)" + "-grams"         
    
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
    print >>sys.stderr, "Writing skip-grams to file"
    totalskipgramcount = 0
    for n in simpleskipgrams:
        totalskipgramcount += sum([ f for f in simpleskipgrams[n].values() ])
    
    f = codecs.open(outputprefix + '.skipgrams', 'w','utf-8')    
    f.write('#N\tSKIP-GRAM\tOCCURRENCE-COUNT\tNORMALISED-IN-NGRAM-CLASS\tNORMALISED-OVER-ALL\tSUBCOUNT\tSUPERCOUNT\n')
    for n in simpleskipgrams:
        for skipgram, count in simpleskipgrams[n]:
            skipgram_s = skipgram[0] + ' * ' + skipgram[1]
            f.write(str(n-2) + '\t' + skipgram_s + '\t' + str(count) + '\t' + str(simpleskipgrams[n].p(skipgram)) + '\t' + str(simpleskipgrams[n][skipgram] / float(totalskipgramcount)) + '\n')

    f.close()


