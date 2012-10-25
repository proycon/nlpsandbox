#! /usr/bin/env python
# -*- coding: utf8 -*-

import codecs
import sys

o = ""

f = codecs.open(sys.argv[1],'r','utf-8')
for line in f:
    for i,c in enumerate(line):
        if c == '&':
            if line[i:i+5] != '&amp;' and line[i:i+1] != '&#':
                #find matching semicolon?
                entity = False
                for c2 in line[i+1:]:
                    if c2 == ';':
                        entity = True
                        break
                    elif not c2.isalnum():
                        break 
                if not entity:
                    o += '&amp;'
                else:
                    o += c
            else:
                o += c        
        else:
            o += c
    o += "\n"                    
f.close()

f = codecs.open(sys.argv[1],'w','utf-8')
f.write(o)
f.close()
