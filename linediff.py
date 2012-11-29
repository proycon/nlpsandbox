#! /usr/bin/env python
# -*- coding: utf8 -*-

import getopt
import sys
import codecs

def usage():
    print >> sys.stderr, "Syntax:  linediff.py files"
    print >> sys.stderr, "Options:"
    print >> sys.stderr, "-e [input encoding]                 - Encoding of input files (utf-8 by default)"
    
def bold(s):
   CSI="\x1B["
   return CSI+"1m" + s + CSI + "0m"
   
def white(s):
   CSI="\x1B["
   return CSI+"37m" + s + CSI + "0m"   


def red(s):
   CSI="\x1B["
   return CSI+"31m" + s + CSI + "0m"
   
def green(s):
   CSI="\x1B["
   return CSI+"32m" + s + CSI + "0m"   


def yellow(s):
   CSI="\x1B["
   return CSI+"33m" + s + CSI + "0m"   

   
def blue(s):
   CSI="\x1B["
   return CSI+"34m" + s + CSI + "0m"   
   

def magenta(s):
   CSI="\x1B["
   return CSI+"35m" + s + CSI + "0m"   

ENCODING = 'utf-8'

try:
    opts, args = getopt.getopt(sys.argv[1:], "e:")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-e':
        ENCODING = a
    else:
        raise Exception("No such option: " + o)
    
files = args    
    
f = []
for filename in files:
    f.append(codecs.open(filename,'r','utf-8') )
    
done = False
linenum = 0
matches = 0
differences = 0
while not done:
    linenum += 1
    lines = []
    hasdata = False
    for i in range(0,len(files)):
        if f[i]:
            lines.append( f[i].readline() )
            if lines[-1]: hasdata = True            
        else:
            lines.append(None)
    
    if not hasdata: 
        done = True
        break

    match = True
    for i, line_i in enumerate(lines):
        for j, line_j in enumerate(lines):
            if line_i != line_j:
                match = False
    
    if match:
        matches += 1
    else:            
        differences += 1
        print bold("@" + str(linenum) + ":")
        
        
        for i, line in enumerate(lines):
            line = line.strip()
            print " #" + str(i) +": ",
            if i == 0:
                reftokens = line.split(' ')
                print line.encode('utf-8')
            else:
                #highlight differences
                tokens = line.split(' ')
                for j, (reftoken, token) in enumerate(zip(reftokens, tokens)):
                    if token == reftoken:
                        print green(token).encode('utf-8'),                    
                    elif (j > 0 and token == reftokens[j-1]) or (j < len(reftokens) -1 and token == reftokens[j+1]):
                        print white(token).encode('utf-8'),
                    elif token in reftokens:
                        print yellow(token).encode('utf-8'),
                    else:
                        print red(token).encode('utf-8'),     
                print                           
            
print >>sys.stderr, "Total lines: ", linenum - 1    
print >>sys.stderr, "Matches: ", matches, str(matches / float(linenum - 1) * 100) + str('%')
print >>sys.stderr, "Differences: ", differences, str(differences / float(linenum - 1) * 100) + str('%')

    
    
    

    
    
        
    


