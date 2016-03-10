#!/usr/bin/env python3

import os
import sys
from pynlpl.formats import folia

corpusdir = '.'

langs = ('nld','eng')

outfiles  = {
        'nld': open('nld.txt','w',encoding='utf-8'),
        'eng': open('eng.txt','w',encoding='utf-8')
}

for i, doc in enumerate(folia.Corpus(corpusdir, 'xml.gz','', lambda fn: os.path.basename(fn).startswith('S-OP_') ,ignoreerrors=True)):
    print("Processing #" + str(i) + ": " + doc.filename ,file=sys.stderr)
    for ca in doc.select(folia.ComplexAlignment):
        sentencepair = {}
        for a in ca.select(folia.Alignment):
            sentencepair[a.cls] = " ".join([ aref.t for aref in a.select(folia.AlignReference,ignore=False)])
        if all([lang in sentencepair for lang in langs]):
            if any([ not text.strip() for text in sentencepair.values()]):
                print("  WARNING: Empty text", text,file=sys.stderr)
                continue
            if any([ '\n' in text for text in sentencepair.values()]):
                print("  WARNING: Newline in text: ", text,file=sys.stderr)
                continue
            for lang, text in sentencepair.items():
                outfiles[lang].write(text+"\n")
        else:
            print("  WARNING: Missing language in sentencepair ", sentencepair,file=sys.stderr)



