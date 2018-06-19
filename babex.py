#!/usr/bin/env python3

import lxml.etree
import sys

ns = {'tei':"http://www.tei-c.org/ns/1.0"}

# Brieven als buit extractor
for filename in sys.argv[1:]:
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        print("Processing " + filename,file=sys.stderr)
        doc = lxml.etree.parse(filename).getroot()
        for par in doc.xpath("//tei:s",namespaces=ns):
            for word in par.xpath("./*",namespaces=ns):
                if word.tag == "{http://www.tei-c.org/ns/1.0}pc":
                    text = "".join(word.xpath(".//text()")).replace("\n","")
                    data.append( (text,'PUNC',text) )
                elif word.tag == "{http://www.tei-c.org/ns/1.0}w":
                    text = "".join(word.xpath(".//text()")).replace("\n","")
                    if not text:
                        print("WARNING: word has no text: " , lxml.etree.tostring(word), file=sys.stderr)
                        continue
                    if 'pos' not in word.attrib:
                        print("WARNING: word has no pos: ",  lxml.etree.tostring(word),file=sys.stderr)
                        continue
                    pos = word.attrib['pos']
                    if pos[-1] != ')': pos += '()'
                    if 'lemma' not in word.attrib:
                        print("WARNING: word has no lemma: " , lxml.etree.tostring(word),file=sys.stderr)
                        continue
                    lemma = word.attrib['lemma']
                    if all( (c.isdigit() for c in text )): lemma = text
                    if pos != 'UNRESOLVED' and lemma != 'UNRESOLVED' and ('part' not in word.attrib):
                        cutoff = 0
                        for i, c in enumerate(reversed(text)):
                            if c.isalnum():
                                cutoff = -1 * i
                                break
                        if cutoff != 0:
                            punct = text[cutoff:]
                            text = text[:cutoff]
                            if len(punct) > 0:
                                homogenous = True
                                for pc in punct[1:]:
                                    if pc != punct[0]:
                                        homogenous = False
                                if homogenous:
                                    punct = punct[0]
                            data.append( (text,pos,lemma) )
                            data.append( (punct,"PUNC",punct) )
                        else:
                            data.append( (text,pos,lemma) )

    begin = 0
    for i, (text,pos, lemma) in enumerate(data):
        if ' ' in lemma: lemma = lemma.replace(' ','_')
        if ' ' in pos: pos = pos.replace(' ','_')
        if ' ' in text: text = text.replace(' ','_')
        if not (text and pos and lemma):
            continue
        print(text + "\t" + lemma + "\t" +  pos)
        if i == len(data) - 1:
            eos = True
        elif text in ('.','?','!'):
            #decide if this is an end-of-sentence
            nexttext = data[i+1][0]
            eos = nexttext[0].isupper()
            begin = i+1
        else:
            eos = False
        if eos:
            print("<utt>")
