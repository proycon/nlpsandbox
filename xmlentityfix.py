#! /usr/bin/env python
# -*- coding: utf8 -*-

import codecs
import sys

o = ""

f = codecs.open(sys.argv[1],'r','utf-8')
for line in f:
    for i,c in enumerate(line):
        if c == '&':
            if line[i:5] != '&amp;':
                o += '&amp;'
            else:
                o += c        
        else:
            o += c
    o += "\n"                    
f.close()

f = codecs.open(sys.argv[1],'w','utf-8')
f.write(o)
f.close()
