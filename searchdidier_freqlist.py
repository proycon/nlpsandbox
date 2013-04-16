#!/usr/bin/env python3

import sys
from pynlpl.statistics import FrequencyList

for filename in sys.argv[1:]:
    f_in = open(filename,'rt',encoding='utf-8')
    freqlist = FrequencyList()
    for line in f_in:
        fields = line.strip().split('\t')
        count = int(fields[1])
        for lemma in fields[0].split(' '):
            freqlist.count(lemma, count)
    f_in.close()
    freqlist.save(filename + '.freqlist')



