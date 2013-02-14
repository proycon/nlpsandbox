#! /usr/bin/env python
# -*- coding: utf8 -*-

from cornetto.cornet import Cornet
import sys

#Usage: cornettoextract.py cornetto-lu-db cornetto-synset-db

print >>sys.stderr, "Loading Cornetto DB (time and memory intensive!)"
c = Cornet()
c.open(sys.argv[1],sys.argv[2])


print >>sys.stderr, "Extracting relations"

#ffor source, target in c._graph.edges():


