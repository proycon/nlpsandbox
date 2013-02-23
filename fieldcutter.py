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
    print >>sys.stderr," -s [expression]  Select rows, expression is may use variables #1...#n for the columns, and operators and,or,not,>,<,!=,== (python syntax)."
    print >>sys.stderr," -S               Compute statistics"
    print >>sys.stderr," -H [column]      Compute histogram on the specified column"
    print >>sys.stderr," -C [char]        Ignore comments, line starting with the specified character. Example: -C #"
    print >>sys.stderr," -n               Number lines"
    print >>sys.stderr," -N               Number fields"


if __name__ == "__main__":
    try:
	    opts, args = getopt.getopt(sys.argv[1:], "f:k:d:e:D:o:is:SH:TC:nN")
    except getopt.GetoptError, err:
	    # print help information and exit:
	    print str(err)
	    usage()
	    sys.exit(2)           
    
    filename = ""
    encoding = "utf-8"
    keepsettings = ""
    deletesettings = ""
    delete = []
    keep = []
    delimiter = " "
    overwriteinput = False
    outputfile = None
    DOSTATS = False
    DOHIST = 0
    select = None
    fieldcount = 0
    commentchar = None
    numberfields = False
    numberlines = False
    
    
    for o, a in opts:
        if o == "-e":	
            encoding = a
        elif o == "-f":	
            filename = a              
        elif o == "-k":	
            keepsettings = a
        elif o == "-d":	
            deletesettings = a      
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
            DOHIST = int(a)
        elif o == '-T':
            delimiter = "\t"
        elif o == '-C':
            commentchar = a
        elif o == '-n':
            numberlines = True
        elif o == '-N':
            numberfields = True            
        else:
            raise Exception("invalid option: " + o)
                    
    if not filename:    
        usage()
        sys.exit(2)

    if not os.path.exists(filename):
        print >>sys.stderr,"No such file: " + filename
        sys.exit(2)
    
    f = codecs.open(filename,'r',encoding)
    for line in f:
        if line.strip() and (not commentchar or line[:len(commentchar)] != commentchar):                    
            fieldcount = len(line.strip().split(delimiter))
            print >>sys.stderr,"Number of fields: ", fieldcount
            break
    f.close()
    
    if DOHIST < 0: DOHIST = fieldcount + DOHIST + 1
    
    if keepsettings:
        for x in keepsettings.split(','):
            if ':' in x:
                low,high = [ int(y) for y in x.split(':') ]                
                if low < 0: low = fieldcount + low + 1
                if high < 0: high = fieldcount + high + 1
                for i in range(low, high + 1):
                    keep.append(i)
            else:
                if int(x) < 0: x = fieldcount + x + 1
                keep.append(x)
    
    if deletesettings:
        for x in deletesettings.split(','):
            if ':' in x:
                low,high = [ int(y) for y in x.split(':') ]                
                if low < 0: low = fieldcount + low + 1
                if high < 0: high = fieldcount + high + 1
                for i in range(low, high + 1):
                    delete.append(i)
            else:
                if int(x) < 0: x = fieldcount + x + 1
                delete.append(x)       
    
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
    
    rowcount_in = 0
    rowcount_out = 0
    f = codecs.open(filename,'r',encoding)
    for line in f:
        rowcount_in += 1
        
        
        if not line.strip() or (commentchar and line[:len(commentchar)] == commentchar):
            rowcount_out += 1
            if outputfile:                       
                f_out.write(line.strip() + "\n")
            else:
                print line.strip().encode(encoding)
            continue
        
        

            
        fields = line.strip().split(delimiter)
        if len(fields) != fieldcount:
            print >>sys.stderr, "Number of columns in line " + str(rowcount_in) + " deviates, expected " + str(fieldcount) + ", got " + str(len(fields)) 
            sys.exit(5)
        
        
        if select:
            currentselect = select
            for i in reversed(range(1,len(fields)+1)):
                isdigit = True
                try:
                    x = float(fields[i-1])
                except:                    
                    isdigit = False
                if isdigit:
                    currentselect = currentselect.replace('#' + str(i), fields[i-1])
                else:
                    currentselect = currentselect.replace('#' + str(i), '"' + fields[i-1].replace('"',"\\\"") + '"')
            if not eval(currentselect):
                continue
    
        rowcount_out += 1
        

        if DOHIST:
            if not fields[DOHIST - 1] in freq:
                freq[fields[DOHIST -1]] = 0
            freq[fields[DOHIST -1]] += 1
            
        if DOSTATS:                    
            for i,field in enumerate(fields):
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
            if numberfields:
                field = str(i) + '=' + field                
            if action == 'keep':
                newfields.append(field)
        s = delimiter.join(newfields)
        
        if outputfile:                       
           if numberlines: f_out.write("@" + str(rowcount_in) + delimiter)
           f_out.write(s + "\n")
        else:
           if numberlines: print "@" + str(rowcount_in) + delimiter,
           print s.encode(encoding)
        
    print >>sys.stderr,"Read " + str(rowcount_in) + " lines, outputted " + str(rowcount_out)
    
    if outputfile:
        f_out.close()
        
    if overwriteinput:
        os.rename(outputfile,filename)
        
    if DOSTATS:
        for i in sorted(sumdata):
            print >>sys.stderr, "column #" + str(i) + " sum="+ str(sumdata[i]) + "\taverage=" + str(sumdata[i] / float(rowcount_out))
    
    if DOHIST:        
        s = float(sum(freq.values()))
        for i, (word, count) in enumerate(sorted(freq.items(), key=lambda x: x[1] * -1)):
            print >>sys.stderr, str(i) + ")\t" + word.encode(encoding) + "\t" + str(count) + "\t" + str(count / s * 100) + '%' 
            
