#!/usr/bin/env python3

import sys
import lxml.etree
import os
import glob
from pynlpl.formats.sonar import CorpusFiles



print("Indexing " + sys.argv[1],file=sys.stderr)

count = 0
for i, foliafile in enumerate(CorpusFiles(sys.argv[1],'folia.xml')):
    cmdifile = foliafile.replace(".folia.xml",".cmdi.xml")
    if not os.path.exists(cmdifile):
        print("WARNING: Missing CMDI for " + foliafile,file=sys.stderr)
        continue
    print("Processing #" + str(i+1) + " -- " + cmdifile + "...",file=sys.stderr)
    doc = lxml.etree.parse(cmdifile).getroot()
    country = None
    for element in doc.xpath("/cmd:CMD/cmd:Components/cmd:SoNaRcorpus/cmd:Text/cmd:Source/cmd:Country",namespaces={'cmd':"http://www.clarin.eu/cmd/"}):
        country = element.text
        pass

    if not country:
        country = "unknown"

    print("\t-> " + country,file=sys.stderr)
    country = country.strip().lower()

    print(foliafile+"\t"+country)
    count += 1

    print("... indexed " + str(count) + " files" ,file=sys.stderr)





