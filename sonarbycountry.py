#!/usr/bin/env python3

import sys
import lxml.etree
import os

index = {}

print("Indexing",file=sys.stderr)
for root, dirs, files in os.walk(sys.argv[1]):
    print("Processing " + root + "...",file=sys.stderr)
    for f in files:
        f = root + f
        if f[-9:] == ".cmdi.xml":
            foliafile = f[:-9] + ".folia.xml"
            if not os.path.exists(foliafile):
                print("WARNING: Missing FoLiA for " + f,file=sys.stderr)
                continue
            doc = lxml.etree.parse(f).getroot()
            for element in doc:
                #element.tag, element.attrib['blah'], element.text
                pass

            country = None
            for element in doc.xpath("//cmd:CMD/cmd::Components/cmd:SoNaRcorpus/Source/Country",namespaces={'cmd':"http://www.clarin.eu/cmd/"}):
                country = element.text()
                pass

            if country:
                country = country.strip.lower()
                if not country in index:
                    index[country] = []

                index[country].append(foliafile)
    print("... index now contains " + str(sum( [ len(x) for x in index.values() ])) + " files" ,file=sys.stderr)




