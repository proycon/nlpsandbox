#! /usr/bin/env python
# -*- coding: utf8 -*-

import sys
import codecs
import getopt
import os

def usage():
    print >>sys.stderr,"Usage: fieldcutter.py -f filename"
    print >>sys.stderr,"Options:"
    print >>sys.stderr," -k [columns]     columns to keep (1-indexed), this is a comma separated list of column numbers, negative numbers are allowed for end-aligned-indices. All others will be deleted"
    print >>sys.stderr," -d [columns]     columns to delete (1-indexed), this is a comma separated list of column numbers, negative numbers are allowed for end-aligned-indices. All others will be kept"
    print >>sys.stderr," -e [encoding]    Encoding of the input file, defaults to utf-8"
    print >>sys.stderr," -D [delimiter]   Field delimiter (space by default)"
    print >>sys.stderr," -T               Set tab as delimiter"
    print >>sys.stderr," -o [outputfile]  Output to file instead of stdout"
    print >>sys.stderr," -i               Outputfile equals inputfile"
    print >>sys.stderr," -s [expression]  Select rows, expression is may use variables $1...$n for the columns, and operators and,or,not,>,<,!=,== (python syntax)"
    print >>sys.stderr," -S               Compute statistics"
    print >>sys.stderr," -H [column]      Compute histogram on the specified column"
    


if __name__ == "__main__":
    try:
	    opts, args = getopt.getopt(sys.argv[1:], "f:k:d:e:D:o:is:SHT")
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
    overwriteinput = False
    outputfile = None
    DOSTATS = False
    DOHIST = False
    select = None
    fieldcount = 0
    for o, a in opts:
        if o == "-e":	
            encoding = a
        elif o == "-f":	
            filename = a              
            f = codecs.open(filename,'r',encoding)
            for line in f:
                if line[0] != '#':                    
                    fieldcount = len(line.strip().split(delimiter))
                    print >>sys.stderr,"Number of fields: ", fieldcount
                    break
            f.close()
        elif o == "-k":	
            for x in a.split(','):
                if ':' in x:
                    low,high = x.split(':')
                    if low < 0: low = fieldcount + int(low) + 1
                    if high < 0: high = fieldcount + int(high) + 1
                    for i in range(int(low), int(high) + 1):
                        keep.append(i)
                else:
                    if int(x) < 0: x = fieldcount + int(x) + 1
                    keep.append(int(x))
        elif o == "-d":	
            for x in a.split(','):
                if ':' in x:
                    low,high = x.split(':')
                    if low < 0: low = fieldcount + int(low) + 1
                    if high < 0: high = fieldcount + int(high) + 1
                    for i in range(int(low), int(high) + 1):
                        delete.append(i)
                else:
                    if int(x) < 0: x = fieldcount + int(x) + 1
                    delete.append(int(x))       
        elif o == '-D':
            delimiter = a
        elif o == '-o':    
            outputfile = a
        elif o == '-s':
            select = a
        elif o == '-i':
            outputfile = filename + ".tmp"
            overwriteinput = True
        elif o == '-S':
            DOSTATS = True
        elif o == '-H':
            DOHIST = True            
        elif o == '-T':
            delimiter = "\t"
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
        
        
    sumdata = {}
    nostats = set()
    freq = {}
    
    if keep:
        print >>sys.stderr, "Fields to keep: ",  " ".join([ str(x) for x in keep])
    if delete:
        print >>sys.stderr, "Fields to delete: ",  " ".join([ str(x) for x in delete])
    
    rowcount = 0
    f = codecs.open(filename,'r',encoding)
    for line in f:
        fields = line.strip().split(delimiter)
        
        if select:
            currentselect = select
            for i in reversed(range(1,len(fields)+1)):
                if fields[i-1].isdigit():
                    currentselect = currentselect.replace('$' + str(i), fields[i-1])
                else:
                    currentselect = currentselect.replace('$' + str(i), '"' + fields[i-1].replace('"','\"') + '"')
            #print >>sys.stderr,"DEBUG=["+ currentselect+"]"
            if not eval(currentselect):
                continue
        rowcount += 1
        
            
        if DOSTATS:
            
            for i, field in enumerate(fields):
                if not i in freq:
                    freq[i] = {}
                    if not field in freq[i]:
                        freq[i][field] = 0
                    freq[i][field] += 1
                    
                    
                if not i in nostats: 
                    if '.' in field:
                        try:
                           x = float(field)
                        except:
                           nostats.add(i)
                           if i in sumdata: del sumdata[i]
                           continue
                    else:
                        try:
                           x = int(field)
                        except:
                           nostats.add(i)
                           if i in sumdata: del sumdata[i]
                           continue                        
                 
                    if not i in sumdata:
                        sumdata[i] = 0
                    sumdata[i] += x
                     
            
        
        newfields = []
        #k = [ x - 1 if x >= 0 else len(fields) + x for x in keep ]
        #d = [ x - 1 if x >= 0 else len(fields) + x for x in delete ]
        for i, field in enumerate(fields):
            action = default 
            if i in keep:
                action = 'keep'
            elif i in delete:
                action = 'delete'
            if action == 'keep':
                newfields.append(field)
        s = delimiter.join(newfields)
        if outputfile:                       
           f_out.write(s + "\n")
        else:
           print s.encode(encoding)
        
    print >>sys.stderr,"Outputted " + str(rowcount) + " lines"
    
    if outputfile:
        f_out.close()
        
    if overwriteinput:
        os.rename(outputfile,filename)
        
    if DOSTATS:
        for i in sorted(sumdata):
            print >>sys.stderr, "column #" + str(i) + " sum="+ str(sumdata[i]) + "\taverage=" + str(sumdata[i] / float(rowcount))
    
    if DOHIST:        
        for i, (word, count) in enumerate(sorted(freq, key=lambda x: x[1] * -1)):
            print >>sys.stderr, str(i) + ")\t" + word.encode(encoding) + "\t" + str(count)
            