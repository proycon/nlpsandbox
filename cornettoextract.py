#! /usr/bin/env python
# -*- coding: utf8 -*-


from cornetto.cornet import Cornet
import sys

#Usage: cornettoextract.py cornetto-lu-db cornetto-synset-db

print >>sys.stderr, "Loading Cornetto DB (time and memory intensive!)"
c = Cornet()
c.open(sys.argv[1],sys.argv[2])


print >>sys.stderr, "Extracting relations"

for lu in c._c_lu_id2lu.values():
    lu_spec = c._lu_to_spec(lu)
    results = c.get_related_lex_units(lu_spec,"1")
    for lu_specsource in results:
        for relation in results[lu_specsource]:
            for lu_selecttarget in results[lu_specsource][relation].iterkeys():
                s = lu_specsource + "\t" + relation + "\t" + lu_selecttarget
                print s.encode('utf-8')



