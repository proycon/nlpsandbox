#!/usr/bin/env python3

import sys

# Brieven als buit extractor
for filename in sys.argv[1:]:
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not (line[0] == "<" and line[-1] == ">"):
                fields = line.split('\t')
                if len(fields) == 2:
                    if all( ( not c.isalnum() for c in  fields[0] ) ):
                        data.append( (fields[0], 'PUNCT', fields[0]) )
                elif len(fields) != 3:
                    print("WARNING: Unexpected column layout:", fields,file=sys.stderr)
                else:
                    text, pos, lemma = fields
                    if all( (c.isdigit() for c in text )): lemma = text
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
