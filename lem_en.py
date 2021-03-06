#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division, absolute_import

import sys
import io
from nltk import pos_tag
import nltk.stem.wordnet as wordnet

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return 'a'
    elif treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('N'):
        return 'n'
    elif treebank_tag.startswith('R'):
        return 'r'
    else:
        return ''

inputfile = sys.argv[1]

lemmatizer = wordnet.WordNetLemmatizer()

with io.open(inputfile + '.lem', 'w',encoding='utf-8') as f_lemma:
    with io.open(inputfile + '.pos', 'w',encoding='utf-8') as f_pos:
        with io.open(inputfile,'r',encoding='utf-8') as f:
            for i, line in enumerate(f):
                print(i,file=sys.stderr)
                posline = []
                lemline = []
                tokens = line.split(' ')
                for token, postag in pos_tag(tokens):
                    posline.append(postag)
                    posforlem = get_wordnet_pos(postag)
                    if posforlem:
                        lemline.append(lemmatizer.lemmatize(token,posforlem))
                    else:
                        lemline.append(token)
                f_lemma.write(" ".join(lemline).strip() + "\n")
                f_pos.write(" ".join(posline).strip() + "\n")


