#!/usr/bin/env python
#-*- coding:utf-8 -*-


from pynlpl.statistics import FrequencyList
from pynlpl.textprocessors import crude_tokenizer, Classer
import sys
import codecs
import asizeof

freqlist = FrequencyList()
f = codecs.open(sys.argv[1], 'r','utf-8')
for line in f:
    line = crude_tokenizer(line.strip())
    freqlist.append(line)    
f.close()

print "FREQLIST:               " ,asizeof.asizeof(freqlist)




classer = Classer(freqlist)
print "CLASSER:                " ,asizeof.asizeof(classer)

classer2 = Classer(freqlist, False,True)
print "CLASSER (ONLY DECODER): " ,asizeof.asizeof(classer2)

freqlist2 = FrequencyList()
f = codecs.open(sys.argv[1], 'r','utf-8')
for line in f:
    line = crude_tokenizer(line.strip())
    freqlist2.append(classer.encodeseq(line))    
f.close()
print "FREQLIST-AFTER-CLASSER: " ,asizeof.asizeof(freqlist2)
