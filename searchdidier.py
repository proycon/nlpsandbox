#!/usr/bin/env python3

import gzip

adjs = ( 'energie','snel','exclusief','waardevol','luxe', 'verkoelend','koel','frissend','fris','aantrekkelijk','absorbeert ','automatisch','beschermend','krachtig','intelligent')

f_out = {}
for adj in adjs:
    f_out[adj].open(adj+'.results','wt',encoding='utf-8')


for filename in sys.argv[1:]:
    for line in gzip.open(sys.argv[1]):
        fields = line.strip().split('\t')
        freq = int(fields[1])
        words = fields[0].strip(' ')
        for word in words:
            if word in adjs:
                print(line + "\t" + str(freq), file=f_out[word])

