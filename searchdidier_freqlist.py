#!/usr/bin/env python3

import sys
from pynlpl.statistics import FrequencyList
import didier


for adj in didiers.adjs:
    f_out[adj].close()
    f_in = open(adj + '.results','rt',encoding='utf-8')
    freqlist = FrequencyList()
    for line in f_in:
        fields = line.strip().split('\t')
        count = int(fields[1])
        for lemma in fields[0].split(' '):
            freqlist.count(lemma, count)
    f_in.close()
    freqlist.save(adj + '.freqlist')



