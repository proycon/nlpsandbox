#!/usr/bin/env python3

from pynlpl.formats import folia

corpusdir = ''

langs = ('nld','eng')

outfiles  = {
        'nld': open('nld.txt','w',encoding='utf-8'),
        'eng': open('eng.txt','w',encoding='utf-8')
}

for doc in folia.Corpus(corpusdir, 'xml.gz','', lambda fn: fn.startswith('S-OP_') ):
    print("Processing ", doc.filename ,file=sys.stderr)
    for ca in doc.select(folia.ComplexAlignment):
        sentencepair = {}
        for a in ca.select(folia.Alignment):
            sentencepair[a.cls] = " ".join([ aref.t for aref in a.select(folia.AlignReference)])
        if all([lang in sentencepairs for lang in langs]):
            for lang, text in sentencepair.items():
                outfiles[lang].write(text+"\n")
        else:
            print("WARNING: Missing language in sentencepair ", sentencepair,file=sys.stderr)



