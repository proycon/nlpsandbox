#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs
import getopt

def usage():
    print >>sys.stderr,"Usage: fieldcutter.py -f filename -k [keep] -d [delete] -e [encoding] [-T|-C|-S] -o [outputfile]"
    print >>sys.stderr,"[keep] and [delete] are lists of fields (0-indexed) to keep or delete, negative numbers are allowed for end-aligned-indices. Numbers are comma seperated, ranges may be specified with a colon.  -T set tabs as delimiter instead of default space, -C sets comma, -S semicolon"
     


if __name__ == "__main__":
    try:
	    opts, args = getopt.getopt(sys.argv[1:], "f:k:d:e:TCSo:")
    except getopt.GetoptError, err:
	    # print help information and exit:
	    print str(err)
	    usage()
	    sys.exit(2)           
    
    filename = ""
    encoding = "utf-8"
    delete = []
    keep = []
    delimiter = " "
    outputfile = None
    for o, a in opts:
        if o == "-e":	
            encoding = a
        elif o == "-f":	
            filename = a              
        elif o == "-k":	
            for x in a.split(','):
                if ':' in x:
                    low,high = x.split(':')
                    for i in range(int(low), int(high) + 1):
                        keep.append(i)
                else:
                    keep.append(int(x))
        elif o == "-d":	
            for x in a.split(','):
                if ':' in x:
                    low,high = x.split(':')
                    for i in range(int(low), int(high) + 1):
                        delete.append(i)
                else:
                    delete.append(int(x))       
        elif o == '-T':
            delimiter = "\t"
        elif o == '-C':
            delimiter = ","            
        elif o == '-S':
            delimiter = ";"        
        elif o == '-o':    
            outputfile = a
        else:
            raise Exception("invalid option: " + o)
                    
    if not filename:    
        usage()
        sys.exit(2)
    
    if keep: 
        default = 'delete'
    else:        
        default = 'keep'
        
    if outputfile:
        f_out = codecs.open(outputfile, 'w',encoding)
        
    
    f = codecs.open(filename,'r',encoding)
    for line in f:
        fields = line.strip().split(delimiter)
        newfields = []
        for i, field in enumerate(fields):
            action = default 
            k = [ x if x >= 0 else len(fields) + x for x in keep ]
            d = [ x if x >= 0 else len(fields) + x for x in delete ]
            if i in k:
                action = 'keep'
            elif i in d:
                action = 'delete'
            if action == 'keep':
                newfields.append(field)
        s = delimiter.join(newfields)
        if outputfile:                       
           f_out.write(s + "\n")
        else:
           print s.encode(encoding)
        
    if outputfile:
        f_out.close()
