#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os

deletelines = set()


for filename in sys.argv[1:]:
    f = open(filename)
    for i, line in enumerate(f):
        line = line.strip()
        if not line or '\r' in line:
            deletelines.add(i)
    f.close()


for filename in sys.argv[1:]:
    f_in = open(filename,'r')
    f_out = open(filename + '.tmp','w')
    for i, line in enumerate(f_in):
        if not i in deletelines:
            f_out.write(line)
    f_in.close()
    f_out.close()
    os.rename(filename + '.tmp', filename)


