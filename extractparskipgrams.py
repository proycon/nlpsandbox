#!/usr/bin/env python3

import argparse
from pynlpl.formats.moses import PhraseTable
from collections import defaultdict




def main():
    parser = argparse.ArgumentParser(description="Skipgram extraction from Moses phrasetable", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('--storeconst',dest='settype',help="", action='store_const',const='somevalue')
    parser.add_argument('-f','--phrasetable', type=str,help="Moses phrasetable", action='store',default="",required=True)
    #parser.add_argument('-g','--', type=str,help="Moses phrasetable", action='store',default="",required=True)
    parser.add_argument('-t','--threshold', type=int,help="How many times should an aligned skipgram pair occur?", action='store',default=1)
    #parser.add_argument('bar', nargs='+', help='bar help')
    args = parser.parse_args()
    #args.storeconst, args.dataset, args.num, args.bar

    skipgrams = defaultdict(int)  #key: (sourceleft, sourceright, targetleft, targetright)

    pt = PhraseTable(args.phrasetable)
    for source_s, targets in pt:
        source = tuple(source_s.split())
        for target_s, scores in targets:
            target = tuple(target_s.split())

            matches = []
            for length in range(1, len(source) - 2):
                for subsource, rightfixed in ( (source[0:length],False) , (source[-length:], True) ):
                    subsource_s = " ".join(subsource)
                    if subsource_s in pt:
                        subtargets = pt[subsource_s]
                        for subtarget, _ in subtargets:
                            subtarget_s = " ".join(subtarget)
                            if target_s.beginswith(subtarget):
                                #we have a match:  x-y -> x'-y'
                                #now see if we can find a y
                                matches.append( (subsource, rightfixed, subtarget, False))
                            elif target_s.endswith(subtarget):
                                #we have a match: x-y -> y'-x'
                                #now see if we can find a y
                                matches.append( (subsource, rightfixed, subtarget, True)) #True=reversed/right-fixed


            #now find matches that complement eachother
            for i, (subsource, rightfixed_source, subtarget, rightfixed_target) in enumerate(matches):
                for j, (subsource2, rightfixed_source2, subtarget2, rightfixed_target2) in enumerate(matches):
                    if i != j and rightfixed_source != rightfixed_source2 and rightfixed_target != rightfixed_target2 and len(subsource) + len(subsource2) < len(source) - 1 and len(subtarget) + len(subtarget2) < len(target) - 1:
                        if rightfixed_source2:
                            sourceleft = " ".join(subsource)
                            sourceright = " ".join(subsource2)
                        else:
                            sourceleft = " ".join(subsource2)
                            sourceright = " ".join(subsource)
                        if rightfixed_target2:
                            targetleft = " ".join(subtarget)
                            targetright = " ".join(subtarget2)
                        else:
                            targetleft = " ".join(subtarget2)
                            targetright = " ".join(subtarget)

                        skipgrams[(sourceleft,sourceright, targetleft, targetright)] += 1

    for (sourceleft, sourceright, targetleft, targetright), count in skipgrams.items():
        if count >= args.threshold:
            print(sourceleft + " {*} " + sourceright + "\t" + targetleft + " {*} " + targetright)


if __name__ == '__main__':
    main()
