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
        source = tuple(source.split())
        for target, scores in targets:
            target = tuple(target.split())
            for length in range(1, len(source) - 2):
                subsource = source[0:length]
                subsource_s = " ".join(subsource)
                if subsource_s in pt:
                    subtargets = pt[subsource_s]
                    for subtarget, _ in subtargets:
                        if target.beginswith(subtarget):
                            #we have a match:  x-y -> x'-y'
                            #now see if we can find a y
                            pass
                        elif target.endswith(subtarget):
                            #we have a match: x-y -> y'-x'
                            #now see if we can find a y
                            pass










if __name__ == '__main__':
    main()
