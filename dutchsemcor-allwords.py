#!/usr/bin/env python3

import sys
from collections import defaultdict
from pynlpl.formats import folia
import lxml.etree

sourcedir = sys.argv[1]
targetdir = sys.argv[2]
annotationfiles = sys.argv[3:]

senses = defaultdict(dict) #docid => id => sense

for annotationfile in annotationfiles:
    doc = lxml.etree.parse(annotationfile).getroot()
    for element in doc.xpath("//token"):
        token_id = element.attrib['token_id']
        doc_id = token_id.split('.')[0]
        senses[doc_id][token_id] = element.attrib['sense']

for docid, data in senses.items():
    doc = folia.Document(file=sourcedir + '/' + docid + ".xml")
    doc.declare(folia.SenseAnnotation, "cornetto")
    for tokenid, sense in data.items():
        doc[tokenid].append( folia.SenseAnnotation(cls=sense) )
    doc.save(targetdir + "/" + docid + ".folia.xml")










