#!/usr/bin/env python3

import gzip
import sys

adjs = ( 'energie','snel','exclusief','waardevol','luxe', 'verkoelend','koel','verfrissend','fris','aantrekkelijk','absorberend','absorberen','automatisch','beschermend','krachtig','intelligent')

f_out = {}
for adj in adjs:
    f_out[adj] = open(adj+'.results','wt',encoding='utf-8')

count = 0
for filename in sys.argv[1:]:
    f_in = open(sys.argv[1])
    for line in f_in:
        count += 1
        if (count % 1000) == 0: print(count,file=sys.stderr)
        line = line.strip()
        fields = line.split('\t')
        freq = int(fields[1])
        lemmas = fields[0].split(' ')
        for lemma in lemmas:
            lemma=lemma.strip().lower()
            if lemma in adjs:
                print(line + "\t" + str(freq), file=f_out[lemma.lower()])
                #print(line)
    f_in.close()

#for adj in adjs:
#    f_out[adj].close()
#    f_in = open(adj + '.results','rt',encoding='utf-8')
#
#    f_in.close()

