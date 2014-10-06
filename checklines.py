#!/usr/bin/env python3

from __future__ import print_function, unicode_literals, division, absolute_import
import sys

for filename in sys.argv[1:]:
    with open(filename,'r',encoding='utf-8') as f:
        for i,line in enumerate(f):
            line = line.strip('\n')
            if not line:
                print("Empty line in " + filename + " @ " + str(i+1),file=sys.stderr)
            elif not line.strip(' \t'):
                print("Only whitespace line in " + filename + " @ " + str(i+1),file=sys.stderr)
            elif '\r' in line:
                print("Carriage return in line in " + filename + " @ " + str(i+1),file=sys.stderr)

