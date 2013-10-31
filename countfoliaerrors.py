#!/usr/bin/env python3

from pynlpl.formats import folia
import sys

try:
    filename = sys.argv[1]
except:
    raise Exception("Specify a FoLiA file")

doc = folia.Document(file=filename)
count = 0
for c in doc.select(folia.Correction):
    print("ORIGINAL " + c.parent.text() + " SUGGESTIONS: " + ",".join([str(x) for x in c.suggestions()]) + " ANNOTATOR: " + c.annotator)
    count += 1
print(count)
