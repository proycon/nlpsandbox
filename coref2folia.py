#! /usr/bin/env python
# -*- coding: utf8 -*-

from pynlpl.formats import folia
import sys

assert folia.FOLIAVERSION[0:2] == '0.9'

try:
    docfilename = sys.argv[1]
    chainsfilename = sys.argv[2]
except:
    print >>sys.stderr, "Usage: coref2folia.py foliadoc.xml chainsfile"
    sys.exit(2)
    
doc = folia.Document(file=docfilename)
doc.declare( folia.AnnotationType.COREFERENCE, set="coreferenceset-ttnww" ) #setnaam beter vervangen door een URL / persistant identifier waar later de echte setdefinitie zou kunnen komen te staan

textbody = doc[0]
assert isinstance(doc[0], folia.Text)

layer = None

f = open(chainsfilename, 'r')
for line in f:
    fields = line.split('\t')
    chainid = fields[0]

    if layer is None:    
        layer = textbody.append(folia.CoreferenceLayer)
    else:
        if chainid:
            chain = layer.append( folia.CoreferenceChain, id=chainid, cls='ident') #Ik neem maar aan dat alles klasse 'ident' heeft??
        else:
            chain = layer.append( folia.CoreferenceChain, cls='ident')
            
        for linkid in fields[1:]:
            chain.append( folia.CoreferenceLink, doc[linkid] ) #geeft exception als de index niet bestaat
        
f.close()

doc.save()

