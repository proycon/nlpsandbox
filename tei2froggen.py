#!/usr/bin/env python3

#optimised for CRM/Corpus Gysseling
#See also babex.py (Brieven als buit)!

from __future__ import print_function, unicode_literals, division, absolute_import
import sys
import lxml.etree


ns = {"tei": "http://www.tei-c.org/ns/1.0"}
eos = True
for filename in sys.argv[1:]:
    print("Processing " + filename,file=sys.stderr)
    doc = lxml.etree.parse(filename).getroot()
    print("\t(loaded)",file=sys.stderr)
    for teidoc in doc.xpath("//tei:TEI", namespaces=ns): #in case input contains multiple docs
        print("\t(found document)",file=sys.stderr)
        for word in teidoc.xpath(".//tei:w", namespaces=ns):
            eos = False
            text = "".join(word.itertext()).strip()
            if text:
                tail = ""
                while text[-1] in ('.','?',',',';') and any(c.isalpha() for c in text): #strip trailing punctiation
                    tail = text[-1] + tail
                    text = text[:-1]
                if text:
                    if '\n' in text:
                        print("\t\tRemoving newline in word: ",  text.replace('\n',"\\n"), file=sys.stderr)
                        text = "⊔".join([x.strip() for x in text.split("\n")])
                        print("\t\t->", text, file=sys.stderr)
                    if ' ' in text:
                        print("\t\tRemoving space in word: ",  text, file=sys.stderr)
                        text = text.replace(' ','⊔') #seems to be customary in the dataset already
                    lemma = word.attrib['lemma'].lower() if 'lemma' in word.attrib else text.lower()
                    if lemma[-1] == '?': lemma = lemma[:-1]
                    if '/' in lemma: lemma = lemma.split('/')[0] #we can't deal with disjunctions! just pick the first one
                    pos = word.attrib['msd']
                    print(text + "\t" + lemma + "\t" + pos)
                if tail:
                    print(tail + "\t" + tail + "\t" + "LET()")
                    if tail[-1] in ('.','?'):
                        #just assume end-of-sentence
                        print("<utt>")
                        eos = True
                elif text and text[-1] in ('.','?'):
                    print("<utt>")
                    eos = True
        if not eos:
            print("<utt>")

