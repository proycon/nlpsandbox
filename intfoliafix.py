#!/usr/bin/env python

import sys

for filename in sys.argv[1:]:
    mergelines = {}
    with open(filename,'r',encoding='utf-8') as f:
        found = None
        batchlines = []
        for i, line in enumerate(f):
            if line.strip().startswith("<t-"):
                if found == i-1:
                    batchlines.append(i)
                elif len(batchlines) > 1:
                    mergelines[batchlines[0]] = batchlines[1:]
                    print([ str(i+1) for i in batchlines],file=sys.stderr)
                    batchlines = []
                found = i

    with open(filename,'r',encoding='utf-8') as f_in:
        with open(filename+'.fixed','w',encoding='utf-8') as f_out:
            buffer = None
            until = i
            for i, line in enumerate(f_in):
                if i in mergelines:
                    buffer = line.strip()
                    until = mergelines[i][-1]
                elif buffer is not None and i <= until:
                    buffer += line.strip()
                    print(buffer, file=f_out)
                    buffer = None
                else:
                    print(line, file=f_out)


