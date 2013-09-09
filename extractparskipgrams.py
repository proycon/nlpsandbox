#!/usr/bin/env python3

import argparse
from pynlpl.formats.moses import PhraseTable

def main():
    parser = argparse.ArgumentParser(description="Skipgram extraction from Moses phrasetable", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('--storeconst',dest='settype',help="", action='store_const',const='somevalue')
    parser.add_argument('-f','--phrasetable', type=str,help="Moses phrasetable", action='store',default="",required=True)
    #parser.add_argument('-g','--', type=str,help="Moses phrasetable", action='store',default="",required=True)
    #parser.add_argument('-i','--number',dest="num", type=int,help="", action='store',default="",required=False)
    #parser.add_argument('bar', nargs='+', help='bar help')
    args = parser.parse_args()
    #args.storeconst, args.dataset, args.num, args.bar


    pt = PhraseTable(args.phrasetable)
    for source, targets in pt:
        for target, scores in targets:
            pass


if __name__ == '__main__':
    main()
