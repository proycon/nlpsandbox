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
from pynlpl.statistics import FrequencyList
from pynlpl.textprocessors import Windower, crude_tokenizer, Classer
from pynlpl.common import log
from networkx import DiGraph, write_gpickle

import getopt
import itertools
import math

def usage():
    print >> sys.stderr, "Extract a phrase list (common n-grams) from a tokenised plain text corpus"
    print >> sys.stderr, "Syntax:  pbmbmt-make-phraselist.py"
    print >> sys.stderr, "Options:"
    print >> sys.stderr, "-f <corpus-file>                 - File name of the TOKENISED plain text corpus file to process"
    print >> sys.stderr, "-t <minimal occurence threshold> - Value indicating the minimal occurence threshold for a n-gram, will be pruned otherwise (default: 2 tokens)"
    print >> sys.stderr, "-T <minimal occurence threshold> - Value indicating the minimal occurence threshold for a skip-gram (total tokens), will be pruned otherwise (default: 2 tokens)"
    print >> sys.stderr, "-Z <minimal occurence threshold> - Value indicating the minimal occurence threshold for a skip in a skip-gram (token per skip), will be pruned otherwise (default: 2 tokens)"
    print >> sys.stderr, "-D <minimal types threshold>     - Value indicating the minimal diversity for a skip-gram (types), will be pruned otherwise (default: at least 2 types)"
    print >> sys.stderr, "-l <minimal length>              - Minimal length of n-grams (default: 2)"    
    print >> sys.stderr, "-L <maximum length>              - Maximum length of n-grams (default: 6)"    
    print >> sys.stderr, "-s                               - compute simple skip-n-grams (output in separate file)"    
    print >> sys.stderr, "-E                               - Enable skip-gram expansion, computes more complex skip-grams (cpu/mem intensive)"    
    print >> sys.stderr, "-C                               - use classer (saves memory and speeds up computation, but only when dealing with large data sets, outputs an extra .cls file)"
    print >> sys.stderr, "-c                               - compute compositional data (memory intensive!)" 
    print >> sys.stderr, "-I                               - maintain and output index file (separate file, memory intensive!)"    
    print >> sys.stderr, "-S                               - Output all possible skips in .skipgram file (no significant cpu/memory cost)"    
    print >> sys.stderr, "-o <output prefix>               - path + filename, .phraselist extension will be added automatically. If not set, will be derived from input file."    
    print >> sys.stderr, "-p                               - Input is not tokenised, apply crude built-in tokeniser."
    print >> sys.stderr, "-e <encoding>                    - Encoding of input file (default: utf-8, note that output is always utf-8 regardless)"    
    
    


corpusfile = outputprefix = None
MINTOKENS = MINSKIPGRAMTOKENS= MINSKIPTOKENS =  MINSKIPTYPES = 2
MINLENGTH = 2
MAXLENGTH = 6
DOSKIPGRAMS = False
DOSKIPOUTPUT = False
DOCOMPOSITIONALITY = False
DOTOKENIZE = False
DOINDEX = False
DOCLASSER = False
DOSKIPGRAMEXPANSION = False
ENCODING = 'utf-8'

try:
    opts, args = getopt.getopt(sys.argv[1:], "f:ht:T:Z:l:L:sco:e:pICD:E")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-f':
        corpusfile = a
    elif o == '-t':
        MINTOKENS = int(a)
    elif o == '-T':
        MINSKIPGRAMOCCURENCES = int(a)    
    elif o == '-Z':
        MINSKIPOCCURENCES = int(a)            
    elif o == '-D':
        MINSKIPTYPES = int(a)
    elif o == '-E':
        DOSKIPGRAMEXPANSION = True
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


def buildclasser():
    global DOTOKENIZE, ENCODING, outputprefix
    log("Counting unigrams (for classer) ...",stream=sys.stderr)
    freqlist = FrequencyList()
    f = codecs.open(corpusfile,'r',ENCODING)
    for i, line in enumerate(f):            
        if (i % 10000 == 0): 
            log("\tLine " + str(i+1) + " - (classer construction)", stream=sys.stderr)
        if DOTOKENIZE: 
            line = crude_tokenizer(line.strip())
        line = line.strip().split(' ')
        freqlist.append(['<begin>'] + line + ['<end>'])
    f.close()
    
    log("Building classer ...", stream=sys.stderr)
    classer = Classer(freqlist)
    classer.save(outputprefix + '.cls')
    log("\t" + str(len(classer)) + " classes found", stream=sys.stderr)
    return classer    

def countngrams(classer, n, freqlist, simpleskipgrams, skips, index, linecount=0):
    global DOTOKENIZE, DOCLASSER, DOSKIPGRAMS, DOINDEX
    log("Counting "+str(n)+"-grams ...", stream=sys.stderr)
    f.seek(0)
    for i, line in enumerate(f):
        if (i % 10000 == 0): 
            if linecount == 0:
                log("\tLine " + str(i+1) + " - (" + str(n) + "-grams)", stream=sys.stderr)
            else:
                log("\tLine " + str(i+1) + " of " + str(linecount) + " - " + str( round(((i+1) / float(linecount)) * 100)) + "% " + " (" + str(n) + "-grams)" , stream=sys.stderr) 
        if DOTOKENIZE: 
            line = crude_tokenizer(line.strip())
        else:
            line = [ x for x in line.strip().split(' ') if x ]
        for ngram in Windower(line,n):
            if DOCLASSER: ngram = tuple(classer.encodeseq(ngram))
            if n - 1 in freqlist:
                count = (ngram[1:] in freqlist[n-1] and ngram[:-1] in freqlist[n-1])
            else:
                count = True
            if count:
                freqlist[n].count(ngram)
                if DOINDEX:
                    try:
                        index[ngram].add(i)
                    except KeyError:
                        index[ngram] = set((i,))
                if DOSKIPGRAMS and n >= 3 and ngram[0] != '<begin>' and ngram[-1] != '<end>':
                    skipgram =  ( (ngram[0],) , (ngram[-1],) )
                    body = tuple(ngram[1:-1])
                    if not skipgram in simpleskipgrams[n]: #using None key for overall count to save computation time later
                        simpleskipgrams[n][skipgram] = {None: 1}
                    else:
                        simpleskipgrams[n][skipgram][None] += 1
                    if body in simpleskipgrams[n][skipgram]:
                        if DOINDEX:
                            simpleskipgrams[n][skipgram][body][0] += 1
                            simpleskipgrams[n][skipgram][body][1].add(i)
                        else:
                            simpleskipgrams[n][skipgram][body] += 1
                    else:
                        if DOINDEX:
                            simpleskipgrams[n][skipgram][body] = [1,set(i)]
                        else:
                            simpleskipgrams[n][skipgram][body] = 1
                    
                    #simpleskipgrams[n].count( skipgram )                     
                    #try:
                    #    skips[skipgram].append( ngram[1:-1] )
                    #except:
                    #    skips[skipgram] = [ ngram[1:-1] ]
    log("Found " + str(len(freqlist[n])) +  " " + str(n) + "-grams", stream=sys.stderr)                    
    return i+1
    
def prunengrams(n, freqlist, simpleskipgrams):
    global DOTOKENIZE, DOCLASSER, DOSKIPGRAMS, MINTOKENS
    log("Pruning " + str(n) + "-grams...", stream=sys.stderr)
    for ngram, count in freqlist[n]:
        if count < MINTOKENS:
            del freqlist[n][ngram]  
            if DOINDEX: 
                del index[ngram]
            if DOSKIPGRAMS:
                skipgram = ( (ngram[0],) , (ngram[-1],) )
                if skipgram in simpleskipgrams[n] and simpleskipgrams[n][skipgram][None] <= count:
                    #note: if skip-grams are not found on the same n-level, they are pruned because of this early-pruning
                    del simpleskipgrams[n][skipgram]   
                    
    log("Retained " + str(len(freqlist[n])) +  " " + str(n) + "-grams after pruning", stream=sys.stderr)                    
    
def pruneskipgrams(n, simpleskipgrams, skips):
        global MINSKIPTYPES, MINSKIPGRAMTOKENS, MINSKIPTOKENS
        l = len(simpleskipgrams[n])
        log("Pruning skip-" + str(n) + "-grams... (" +str(l)+")", stream=sys.stderr)
        for i, (skipgram, data) in enumerate(simpleskipgrams[n].items()):
            if i % 10000 == 0:  log('\t\t@' + str(i),stream=sys.stderr)
            typecount = len(data) - 1 #Minus the meta None/count entry
            prune = False
            if typecount < MINSKIPTYPES or data[None] < MINSKIPGRAMTOKENS:
                prune = True
            else:
                cacheditems = data.items()
                modified = False
                for skip,data2 in list(data.items()):
                    if DOINDEX:
                        count = data2[0]
                    else:
                        count = data2
                    if count < MINSKIPTOKENS:
                        modified = True
                        #prune this skip-content only
                        simpleskipgrams[n][skipgram][None] -= count
                        del simpleskipgrams[n][skipgram][skip] 
                del cacheditems
                
                if modified:
                    #recompute, things have changed
                    typecount = len(simpleskipgrams[n][skipgram]) - 1 #Minus the meta None/count entry
                    if typecount < MINSKIPTYPES or simpleskipgrams[n][skipgram][None] < MINSKIPGRAMTOKENS:
                        prune = True

            if prune:
                del simpleskipgrams[n][skipgram]
        log("\t" +str(len(simpleskipgrams[n])) + " left after pruning",stream=sys.stderr)
    
def expandskipgrams(n, simpleskipgrams, skips):
    log("Expanding skip-" + str(n) + "-grams...",stream=sys.stderr)
    cacheitems = list(simpleskipgrams[n].items())
    expansionsize = 0
    for p, (skipgram, data) in enumerate(cacheitems):
        if p % 1000 == 0:  log( '\t\t@' + str(p) + ' - ' + str(expansionsize) + ' new skip-grams thus-far',stream=sys.stderr)
        if len(data) ** 2 >= 1000000:
            log( '\t\t\t@' + str(p) + ' -- ' + str(len(data)**2) + ' comparisons',stream=sys.stderr)

        processed = {}
        skipdata = data.items()
        for skip, skipcontent in skipdata:            
            if skip:
                for skip2, skipcontent2 in skipdata:                        
                    if skip != skip2 and skip2 and not (skip2,skip) in processed:
                        processed[(skip,skip2)] = True
                        left = []
                        right = []
                        position = 0
                        consecutive = True
                        gap = 0
                        prev = None
                        gapbegin = 0
                        gapsize = 1
                        for i in xrange(0,len(skip)):
                            w = skip[i]
                            if w == skip2[i]:
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

        if len(data) ** 2 >= 1000000:
            log( '\t\t\t(next)',stream=sys.stderr)               

    log("Found " + str(len(simpleskipgrams[n])) + " skip-" + str(n) + "-grams, of which "+str(expansionsize) + " from expansion step)", stream=sys.stderr)
    
def buildcompgraph(freqlist):
    compgraph = DiGraph()
    for n in freqlist:
        log("Computing compositionality graph (processing " +str(n) + "-grams)", stream=sys.stderr)
        l = len(freqlist[n])
        for i, (ngram, count) in enumerate(freqlist[n]):
            if (i % 10000 == 0): 
                log('\t' + str(float(round((i/float(l))*100,2))) + '%',stream=sys.stderr)
            for n2 in range(MINLENGTH,n):
                for subngram in Windower(ngram,n2):
                    if subngram in freqlist[n2]:
                        compgraph.add_edge(subngram, ngram)        

    log("Writing compositionality graph to file", stream=sys.stderr)

    write_gpickle(compgraph, outputprefix + '.compgraph')
    return compgraph

if DOCLASSER:
    classer = buildclasser()
else:
    classer = None

f = codecs.open(corpusfile,'r',ENCODING)
freqlist = {}
if DOINDEX: index = {}
simpleskipgrams = {}
linecount = 0
for n in xrange(MINLENGTH,MAXLENGTH+1):
    
    freqlist[n] = FrequencyList(None,True,False) #tokens=None, casesensitive=True, dovalidation=False

    simpleskipgrams[n] = {}
    skips = {}
    
    #Count n-grams
    linecount = countngrams(classer, n, freqlist, simpleskipgrams, skips, index)
                            
    if MINTOKENS > 1:
        #prune n-grams
        prunengrams(n, freqlist, simpleskipgrams)
    
    

    if DOSKIPGRAMS:
        pruneskipgrams(n, simpleskipgrams, skips)
        
        if DOSKIPGRAMEXPANSION:
            #Expand skip-grams
            expansionsize = 0
            if n > 3:
                expandskipgrams(n, simpleskipgrams, skips)
                
                pruneskipgrams(n, simpleskipgrams, skips)
        
            
    
if DOCOMPOSITIONALITY:
    compgraph = buildcompgraph(freqlist)
    



totalcount = 0
for n in freqlist:
    totalcount += sum([ f for f in freqlist[n].values() ])
            
log("Writing n-grams to file", stream=sys.stderr)

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
    log("Writing skip-n-grams to file", stream=sys.stderr)
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
            for skip, skipcontent in data.items():
                if skip:
                    skips += 1
                    if DOINDEX:
                        skipcount = skipcontent[0]
                    else:
                        skipcount = skipcontent                    
                    totalskipcount += skipcount                                              
                    entropy += skipcount * -math.log(skipcount)                                                          
                    if DOSKIPOUTPUT:
                        if DOCLASSER:
                            skipoutput += '|'.join(classer.decodeseq(skip)) + ' '
                        else:
                            skipoutput += '|'.join(skip) + ' '
                        skipoutput = skipoutput.rstrip()
            f.write(str(n) + '\t' + skipgram_s + '\t' + str(count) + '\t' + str(count / float(totalskipgramcount)) + '\t' + str(skips) + '\t' + str(totalskipcount) + '\t' + str(entropy) + '\t' + skipoutput + '\n')
            

    f.close()
    
if DOINDEX:
    log("Writing n-gram index to file", stream=sys.stderr)
    f = codecs.open(outputprefix + '.phraselist.index', 'w','utf-8')        
    f.write('#N-GRAM\tLINES\n')
    for n in freqlist:
        for ngram, count in freqlist[n]:
            if DOCLASSER:
                ngram_s = " ".join(classer.decodeseq(ngram))        
            else:
                ngram_s = " ".join(ngram)                
            f.write( ngram_s + "\t" + " ".join( (str(i) for i in index[ngram] ) ) + '\n')
    f.close()
    
    if DOSKIPGRAMS:
            log("Writing skip-gram index to file", stream=sys.stderr)
            f = codecs.open(outputprefix + '.skipgrams.index', 'w','utf-8')        
            f.write('#SKIP-GRAM\tLINES\n')
            for n in simpleskipgrams:
                                
                for skipgram, data in simpleskipgrams[n].items():
                    if DOCLASSER:
                        skipgram_s = " ".join(classer.decodeseq(skipgram[0])) + " * " + " ".join(classer.decodeseq(skipgram[-1]))
                    else:
                        skipgram_s = " ".join(skipgram[0]) + " * " + " ".join(skipgram[-1])  
                    skipindex = [ skipcontent[0] for skip, skipcontent in data.items() ]
                    f.write( skipgram_s + "\t" + " ".join( (str(i) for i in skipindex) ) + '\n')        
            f.close()

