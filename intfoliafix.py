#!/usr/bin/env python

import sys

mergelines = []
for filename in sys.argv[1:]:
    with open(filename,'r',encoding='utf-8') as f:
        found = None
        batchlines = []
        for i, line in enumerate(f):
            if line.strip().startswith("<t-"):
                if found == i-1:
                    batchlines.append(i)
                else:
                    batchlines = []
                    mergelines.append(batchlines)
                found = i

for lines in mergelines:
    print([ str(i+1) for i in lines],file=sys.stderr)
