#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs

f = codecs.open(sys.argv[1],'r', 'utf-8')
lines1 = list( f.readlines())
f.close()

f = codecs.open(sys.argv[2],'r', 'utf-8')
lines2 = list(f.readlines())
f.close()

f1 = codecs.open(sys.argv[3],'w', 'utf-8')
f2 = codecs.open(sys.argv[4],'w', 'utf-8')

for line1,line2 in zip(lines1, lines2):
    line1 = line1.strip()
    line2 = line2.strip()
    if line1[0] != '<' and line2[0] != '<' and line1[-1] != '>' and line2[-1] != '>':
        f1.write(line1+"\n")
        f2.write(line2+"\n")
        
f1.close()
f2.close()
    
    


