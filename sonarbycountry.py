#!/usr/bin/env python3

import sys
import lxml.etree
import os

index = {}

print("Indexing",file=sys.stderr)
for root, dirs, files in os.walk(sys.argv[1]):
    print("Processing " + root + "... (" + str(len(files)) + " files)",file=sys.stderr)
    for f in files:
        f = os.path.join(root,f)
        if f[-9:] == ".cmdi.xml":
            foliafile = f[:-9] + ".folia.xml"
            if not os.path.exists(foliafile):
                print("WARNING: Missing FoLiA for " + f,file=sys.stderr)
                continue
            print("\tReading " + f + "...",file=sys.stderr)
            doc = lxml.etree.parse(f).getroot()
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




