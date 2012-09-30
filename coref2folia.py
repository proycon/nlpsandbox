#! /usr/bin/env python
# -*- coding: utf8 -*-

from pynlpl.formats import folia
import sys

assert folia.FOLIAVERSION[0:3] == '0.9'

try:
    docfilename = sys.argv[1]
    chainsfilename = sys.argv[2]
except:
    print >>sys.stderr, "Usage: coref2folia.py foliadoc.xml chainsfile"
    sys.exit(2)
    
doc = folia.Document(file=docfilename)
doc.declare( folia.AnnotationType.COREFERENCE, set="coreferenceset-ttnww",annotator="coreference-annotator-gent",annotatortype=folia.AnnotatorType.AUTO) #setnaam beter vervangen door een URL / persistant identifier waar later de echte setdefinitie zou kunnen komen te staan. LET OP! Annotator vervangen door de naam van jullie tooltje


textbody = doc[0]
assert isinstance(doc[0], folia.Text)

layer = None

f = open(chainsfilename, 'r')
for line in f:
    line = line.strip()
    if line:
        fields = line.split('\t')
        chainid = fields[0]
        print "processing chain: ", chainid
        chunks = fields[1].split(' ')

        if layer is None:    
            layer = textbody.append(folia.CoreferenceLayer)
    
        if chainid.isdigit():
            chainid = doc.id + ".dependencychain." + str(chainid)            
        if chainid:
            chain = layer.append( folia.CoreferenceChain, id=chainid, cls='ident') #Ik neem maar aan dat alles klasse 'ident' krijgt?? Anders kan je de klasse ook gewoon weggooien heir
        else:
            chain = layer.append( folia.CoreferenceChain, cls='ident')
                                    
        for chunk in chunks:
            print "\tprocessing chunk: ", chunk
            words = []
            for linkid in chunk.split(','):
                words.append(doc[linkid])
            print "\t(gathered " + str(len(words)) + " words)"
            chain.append( folia.CoreferenceLink, *words ) #geeft exception als de index niet bestaat
        
f.close()

doc.save()

