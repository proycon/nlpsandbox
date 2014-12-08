#!/usr/bin/env python3

import sys

def makefolds(filename, folds):
    with open(filename, 'r', encoding='utf-8') as fin:
        prefix = filename.replace('.txt','').replace('.train','')
        fold = {}
        foldconfig = open(prefix+ '.folds','w', encoding='utf-8') #will hold the fold-containing files, one per line.. as timbl likes it
        for i in range(0,folds):
            fold[i] = open(prefix + '.fold' + str(i), 'w', encoding='utf-8')
            foldconfig.write(prefix + '.fold' + str(i) + '\n')
        foldconfig.close()
        #make folds:
        for i, line in enumerate(fin):
            f = i % folds
            fold[f].write(line)
        for f in fold.values():
            f.close()

if __name__ == '__main__':
    try:
        folds = int(sys.argv[2])
    except:
        folds = 10

    makefolds(sys.argv[1])
