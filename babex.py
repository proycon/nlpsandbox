#!/usr/bin/env python3

import lxml.etree
import sys
for element in doc:
    #element.tag, element.attrib['blah'], element.text
    pass
for element in doc.xpath("//test"):
    pass

ns = {'tei':"http://www.tei-c.org/ns/1.0"}

# Brieven als buit extractor
for filename in sys.argv[1:]:
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        doc = lxml.etree.parse(filename).getroot()
        for word in doc.xpath("//tei:w",namespaces=ns):
            text = word.text
            pos = word.attrib['type']
            lemma = word.attrib['lemma']
            if pos != 'UNRESOLVED' and lemma != 'UNRESOLVED' and word.attrib['xtype'] != 'multiw':
                for i, c in enumerate(reversed(text)):
                    if c.isalnum():
                        cutoff = -1 * i
                if cutoff != 0:
                    punct = text[cutoff:]
                    text = text[:cutoff]
                    data.append( (text,pos,lemma) )
                    data.append( (punct,"PUNC",punct) )
                else:
                    data.append( (text,pos,lemma) )

    begin = i
    for i, (text,pos, lemma) in enumerate(data):
        print(text + "\t" + lemma + "\t" +  pos)
        if text == '.':
            #decide if this is an end-of-sentence
            if i == len(data):
                eos = True
            else:
                eos = text[i+1][0].isupper()
                begin = i+1
            if eos:
                print("<utt>")
