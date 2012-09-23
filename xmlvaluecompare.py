#! /usr/bin/env python
# -*- coding: utf8 -*-

import lxml.etree
import sys
from collections import Counter


def nons(s):
    copy = True
    s2 = ""
    for c in s: 
        if c == '{':
            copy = False
        if copy:                        
            s2 += c
        if c == '}':
            copy = True
    return s2

def getpath(e):
    ancestors= []
    for e in e.iterancestors():
        ancestors.append(e)
    ancestors.reverse()
    return "/" + "/".join( ( nons(x.tag) for x in ancestors ) )                

def revindex(e, index):
    path = getpath(e)
    if e.text and e.text.strip():
        if not e.text in index:
            index[e.text] = Counter()
        index[e.text][path] += 1 
    
    for attrib, value in e.attrib.items():
        if not value in index:   
            index[value] = Counter()
        index[value][path+ '/@' + nons(attrib)] += 1
        
    for element in e:
        revindex(element, index)
        

def xmlcompare(filename1, filename2, diffonly):
    #mapping = {} #source => target => count
    
    doc1 = lxml.etree.parse(filename1)
    revindex1 = {}
    revindex(doc1.getroot(), revindex1) #value => [element/attr]
    
    doc2 = lxml.etree.parse(filename2)
    revindex2 = {}
    revindex(doc2.getroot(), revindex2) #value => [element/attr]
    
    #values in source and not in target
    for value in set( set(revindex1.keys()) | set(revindex2.keys()) ):
        if value in revindex1 and value in revindex2: 
            if not diffonly:
                print "== \"" + value.encode('utf-8') + "\":"
                for path, count in revindex1[value].items():
                    print "\t<=" + path + " -- ", count    
                for path, count in revindex2[value].items():
                    print "\t>=" + path + " -- ", count                    
        elif value in revindex1:
            print "<< \"" + value.encode('utf-8') + "\":"
            for path, count in revindex1[value].items():
                print "\t<" + path + " -- ", count
        elif value in revindex2:
            print ">> \"" + value.encode('utf-8') + "\":"
            for path, count in revindex2[value].items():
                print "\t>" + path + " -- ", count
            
def usage():
    print >>sys.stderr,"Syntax: xmlvaluecompare.py sourcefile targetfile"
    sys.exit(2)

if __name__ == "__main__": 
    import getopt
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dh")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    diffonly = False

    for o, a in opts:
        if o == '-d':
            diffonly = True
        elif o == '-h':
            usage()
        
    try:
        filename1 = args[0]
        filename2 = args[1]
    except:
        usage()        
    xmlcompare(filename1,filename2, diffonly)
    
