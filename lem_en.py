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
            for line in f:
                posline = []
                lemline = []
                tokens = line.split(' ')
                postags = pos_tag(tokens)
                for token, postag in zip(tokens,postags):
                    posline.append(postag)
                    lemline.append(lemmatizer.lemmatize(token,postag))
                f_lemma.write(" ".join(lemline))
                f_pos.write(" ".join(posline))


