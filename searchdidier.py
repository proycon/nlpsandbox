#!/usr/bin/env python3

import gzip
import sys

adjs = ( 'energie','snel','exclusief','waardevol','luxe', 'verkoelend','koel','frissend','fris','aantrekkelijk','absorbeert ','automatisch','beschermend','krachtig','intelligent')

f_out = {}
for adj in adjs:
    f_out[adj] = open(adj+'.results','wt',encoding='utf-8')


for filename in sys.argv[1:]:
    f_in = open(sys.argv[1])
    for line in f_in:
        fields = line.strip().split('\t')
        freq = int(fields[1])
        lemmas = fields[0].strip(' ')
        for lemma in lemmas:
            if lemma.lower() in adjs:
                print(line + "\t" + str(freq), file=f_out[lemma.lower()])
    f_in.close()
