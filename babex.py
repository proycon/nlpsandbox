#!/usr/bin/env python3

import sys

# Brieven als buit extractor
for filename in sys.argv[1:]:
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not (line[0] == "<" and line[-1] == ">"):
                fields = line.split('\t')
                if len(fields) != 3:
                    print("WARNING: Unexpected column layout:", fields,file=sys.stderr)
                else:
                    text, pos, lemma = fields
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
