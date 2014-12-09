#!/usr/bin/env python3

import sys
import lxml.etree
import os
import glob
from pynlpl.formats.sonar import CorpusFiles

index = {}

print("Indexing",file=sys.stderr)

for i, foliafile in enumerate(CorpusFiles(sys.argv[1])):
    cmdifile = foliafile.replace(".folia.xml",".cmdi.xml")
    if not os.path.exists(cmdifile):
        print("WARNING: Missing CMDI for " + foliafile,file=sys.stderr)
        continue
    print("Processing #" + str(i) + " -- " + cmdifile + "...",file=sys.stderr)
    doc = lxml.etree.parse(cmdifile).getroot()
    country = None
    for element in doc.xpath("//cmd:CMD/cmd::Components/cmd:SoNaRcorpus/cmd:Text/cmd:Source/cmd:Country",namespaces={'cmd':"http://www.clarin.eu/cmd/"}):
        country = element.text()
        pass

    if not country:
        country = "unknown"

    print("\t-> " + country,file=sys.stderr)
    country = country.strip.lower()
    if not country in index:
        index[country] = []

    index[country].append(foliafile)

    print("... index now contains " + str(sum( [ len(x) for x in index.values() ])) + " files" ,file=sys.stderr)




