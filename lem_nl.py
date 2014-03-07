#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division, absolute_import

import sys
import io
from pynlpl.clients.frogclient import FrogClient



frogclient = FrogClient('localhost',12345)

inputfile = sys.argv[1]


with io.open(inputfile + '.lem', 'w',encoding='utf-8') as f_lemma:
    with io.open(inputfile + '.pos', 'w',encoding='utf-8') as f_pos:
        with io.open(inputfile,'r',encoding='utf-8') as f:
            for i, line in enumerate(f):
                print(i,file=sys.stderr)
                posline = []
                lemline = []
                for word,lemma,morph,pos in frogclient.process(line.strip()):
                    posline.append(pos)
                    lemline.append(lemma)
                f_lemma.write(" ".join(lemline).strip() + "\n")
                f_pos.write(" ".join(posline).strip() + "\n")


