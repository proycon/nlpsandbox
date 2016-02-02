#! /usr/bin/env python3
# -*- coding: utf8 -*-

from __future__ import print_function, unicode_literals, division, absolute_import

import getopt
import sys

def usage():
    print("Syntax:  linediff.py files", file=sys.stderr)
    print("Options:", file=sys.stderr)
    print("-e [input encoding]                 - Encoding of input files (utf-8 by default)", file=sys.stderr)

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
except getopt.GetoptError as err:
    print(err, file=sys.stderr)
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
    f.append(open(filename,'r',encoding='utf-8') )

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
        print(bold("@" + str(linenum) + ":"))


        for i, line in enumerate(lines):
            line = line.strip()
            print(" #" + str(i) +": ",end="")
            if i == 0:
                reftokens = line.split(' ')
                print(line)
            else:
                #highlight differences
                tokens = line.split(' ')
                for j, (reftoken, token) in enumerate(zip(reftokens, tokens)):
                    if token == reftoken:
                        print(green(token), end=" ")
                    elif (j > 0 and token == reftokens[j-1]) or (j < len(reftokens) -1 and token == reftokens[j+1]):
                        print(white(token), end=" ")
                    elif token in reftokens:
                        print(yellow(token),end=" ")
                    else:
                        print(red(token), end=" ")
                if len(tokens) > len(reftokens):
                    for token in tokens[len(reftokens):]:
                        if token in reftokens:
                            print(yellow(token),end=" ")
                        else:
                            print(red(token), end=" ")
                print()

print("Total lines: ", linenum - 1, file=sys.stderr)
print("Matches: ", matches, str(matches / float(linenum - 1) * 100) + str('%'), file=sys.stderr)
print("Differences: ", differences, str(differences / float(linenum - 1) * 100) + str('%'), file=sys.stderr)











