#!/usr/bin/python
# PBMBMT: PHRASE-BASED MEMORY-BASED MACHINE TRANSLATOR
# by Maarten van Gompel (proycon)
#   proycon AT anaproy DOT NL
#   http://proylt.anaproy.nl
# Licensed under the GNU Public License v3
# ---------------------------
# Extracts common phrases (n-grams) from one or more corpora

import sys
from pynlpl.statistics import FrequencyList, Distribution

if len(sys.argv) < 2 or sys.argv[1] == "-h":
	print >> sys.stderr, "Extract a phrase list (common n-grams) from a tokenised plain text corpus"
	print >> sys.stderr, "\tSyntax: pbmbmt-make-phraselist.py <corpus-file> [minoccurrences] [minlength] [maxlength]"
	print >> sys.stderr, "\tDefaults: minimum occurrences = 2, mininum phrase length = 2, maximum phrase length = 10"
	print >> sys.stderr, "\tOutput: phrase-count   phrase-frequency     n   phrase"
	sys.exit(1)



if len(sys.argv) >= 3:
	MINOCCURRENCES = int(sys.argv[2])
else:
    MINOCCURRENCES = 2

if len(sys.argv) >= 4:
	MINLENGTH = int(sys.argv[3])
else:
    MINLENGTH = 2

if len(sys.argv) >= 5:
	MAXLENGTH = int(sys.argv[4])
else:
    MAXLENGTH = 6


f = open(sys.argv[1])
freqlist = {}
dist = {}
linecount = 0
for n in xrange(MINLENGTH,MAXLENGTH+1):
    freqlist[n] = FrequencyList(n)
    print >> sys.stderr, "Counting ",n,"-grams ..."
    f.seek(0)
    for i, line in enumerate(f):
        for ngram in Windower(line,n):
            if n - 1 in freqlists:
                count = (ngram[-1:] in freqlists[n-1] and ngram[:-1] in freqlists[n-1])
            else:
                count = True
            if count:
                freqlist[n].count(ngram)
        
    if MINOCCURRENCES > 1:
        print >> sys.stderr, "Pruning..."
        for item, count in freqlist[n]:
            if count < MINOCCURENCES:
                del freqlist[n][item]        


totalcount = sum([ len(f) for f in freqlist.values() ])
            
print >> sys.stderr, "Outputting (unordered)"
for n in freqlist:
    for ngram in freqlist[n]:
        ngram_s = " ".join(ngram)    
        print ngram_s + '\t' + str(freqlist[n][ngram]) + '\t' + str(freqlist[n].p(ngram)) + '\t' + str(freqlist[n][ngram] / float(totalcount))





