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
    for result in c.get_related_lex_units(lu_spec,"1"):
        for lu_specsource in result:
            print >>sys.stderr, "Processing " + lu_specsource
            for relation in result[lu_specsource]:
                print >>sys.stderr, "   Found " + relation
                for lu_selecttarget in result[lu_specsource][relation].iterkeys():
                    print >>sys.stderr,"       with " + lu_selecttarget
                    print lu_specsource + "\t" + relation + "\t" + lu_selecttarget



