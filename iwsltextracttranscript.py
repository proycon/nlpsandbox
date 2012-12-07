#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs

copy = False 
f = codecs.open(sys.argv[1],'r')
for line in f:
    line = line.strip()
    if line.strip() == "<transcript>":
        copy = True
    elif line.strip() == "</transcript>":
        copy = False
    elif copy:
        print line
f.close()
