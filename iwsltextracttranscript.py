#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs

# copy = False 
# f = codecs.open(sys.argv[1],'r')
# for line in f:
    # line = line.strip()
    # if line.strip() == "<transcript>":
        # copy = True
    # elif line.strip() == "</transcript>":
        # copy = False
    # elif copy:
        # print line
# f.close()



f = codecs.open(sys.argv[1],'r')
lines1 = f.readlines()
f.close()

f = codecs.open(sys.argv[2],'r')
lines2 = f.readlines()
f.close()

f1 = codecs.open(sys.argv[3],'w')
f2 = codecs.open(sys.argv[4],'w')

for line1,line2 in zip(lines1, lines2):
    line1 = line1.strip()
    line2 = line2.strip()
    if line1[0] != '<' and line2[0] != '<' and line1[-1] != '>' and line2[-1] != '>':
        f1.write(line1)
        f2.write(line2)
        
f1.close()
f2.close()
    
    











for line in f:
    line = line.strip()
    if line.strip() == "<transcript>":
        copy = True
    elif line.strip() == "</transcript>":
        copy = False
    elif copy:
        print line
