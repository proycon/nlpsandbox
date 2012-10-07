#! /usr/bin/env python
# -*- coding: utf8 -*-

import lxml.etree
import sys
from collections import Counter
import glob
import os

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
        

def xmlcompare(filename1, filename2, diffonly, revindex1, revindex2):
    print "#Comparing " + filename1 + " with " + filename2
    #mapping = {} #source => target => count
    
    doc1 = lxml.etree.parse(filename1)
    revindex(doc1.getroot(), revindex1) #value => [element/attr]
    
    doc2 = lxml.etree.parse(filename2)
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

def addmapping(mapping, missing, revindex1, revindex2):
    for value in set( set(revindex1.keys()) | set(revindex2.keys()) ):
        if value in revindex1 and value in revindex2: 
            for path, count in revindex1[value].items():
                for path2, count2 in revindex2[value].items():    
                    mapping[(path,path2)] += 1              
        elif value in revindex1:
            for path, count in revindex1[value].items():
                missing[path] += 1 
                
def process(dir, diffonly, sourceext,targetext, mapping, missing):
    print "#Processing " + dir
    for f in glob.glob(dir + '/*'):
        if f[-len(sourceext):] == sourceext:            
            targetf = f[:-len(sourceext)] + targetext
            if os.path.exists(targetf):
                revindex1 = {}
                revindex2 = {}                
                xmlcompare(f, targetf, diffonly, revindex1, revindex2)
                addmapping(mapping,missing, revindex1,revindex2)
            else:
                print "#Warning: No target file " + targetf
        elif os.path.isdir(f):
            process(f, diffonly, sourceext, targetext, mapping,missing)
            
def usage():
    print >>sys.stderr,"Syntax: xmlvaluecompare.py sourcefile targetfile"
    print >>sys.stderr,"Options:"
    print >>sys.stderr,"    -d           Show differences only"
    print >>sys.stderr,"Process multiple files in batch, aggregate results:"
    print >>sys.stderr,"    -s [ext]     Source extension"
    print >>sys.stderr,"    -t [ext]     Target extension"
    print >>sys.stderr,"    -D           Directory"
    sys.exit(2)

if __name__ == "__main__": 
    import getopt
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dhs:t:D:")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    diffonly = False
    sourceext = targetext = ""
    dir = None

    for o, a in opts:
        if o == '-d':
            diffonly = True
        elif o == '-h':
            usage()
        elif o == '-s':
            sourceext = a
        elif o == '-t':
            targetext = a
        elif o == '-D':
            dir = a

    revindex1 = {}
    revindex2 = {}
    mapping = {}
    missing = {}

    if sourceext and sourceext[0] != '.':
        sourceext = '.' + sourceext
    if targetext and targetext[0] != '.':
        targetext = '.' + targetext

    if dir and sourceext and targetext:            
        process(dir, diffonly, sourceext, targetext, mapping, missing)
        
        print
        print "#Possible mappings"
        for pathpair, doccount in mapping.items():
            sourcepath, targetpath = pathpair
            print "! " + sourcepath + " == " + targetpath + "  (" + str(doccount) + ")"
            
            
            
        print
        print "#Possibly unmapped:"            
        for path, doccount in missing.items():
            print "? " + path + "  (" + str(doccount) + ")"
                    
    else:        
        try:
            filename1 = args[0]
            filename2 = args[1]
        except:
            usage()        
        xmlcompare(filename1,filename2, diffonly, revindex1, revindex2)
        
    
