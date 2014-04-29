#!/usr/bin/env python3

import sys

for line in open(sys.argv[1], 'r', encoding='utf-8'):
    line = line.strip()
    if line:
        fields = line.split('\t')
        print(fields[1] + '|' + fields[4],end=" ")
    else:
        print()




