#!/usr/bin/env python3

import socket
import argparse
import os
import sys
import glob
from pynlpl.formats import folia

#start an alpino server as follows:
#!/bin/sh
#export PORT=4343
#export TIMEOUT=60000
#export MEMLIMIT=1500M
#export TMPDIR=/tmp
## this one is for parsing
#PROLOGMAXSIZE=${MEMLIMIT} ${ALPINO_HOME}/bin/Alpino -notk -fast user_max=${TIMEOUT}\
# server_kind=parse\
# server_port=${PORT}\
# assume_input_is_tokenized=on\
# debug=1\
# end_hook=xml\
#-init_dict_p\
# batch_command=alpino_server 2> ${TMPDIR}/alpino_server.log &
#echo "Alpino started"


def alpino_parse(sent, host='localhost', port=4343):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    sent = sent + "\n\n"
    s.sendall(sent.encode('utf-8'))
    total_xml=[]
    while True:
        xml = s.recv(8192)
        if not xml:
            break
        total_xml.append(str(xml,encoding='utf8'))

    return "".join(total_xml)


def process_dir(d, extension, outputdir, basedir, useprefix):
    print("Processing directory " + d,file=sys.stderr)
    for f in glob.glob(os.path.join(d,'*')):
        if os.path.isdir(f) and f not in ('.','..'):
            process_dir(f, extension, outputdir, basedir, useprefix)
        elif f.endswith(extension):
            print("Processing file " + f,file=sys.stderr)
            try:
                doc = folia.Document(file=f)
            except Exception as e:
                print("PARSING ERROR: ", str(e),file=sys.stderr)
                continue
            process_folia(doc, outputdir, f.replace(basedir,"").replace("/","_") + "-" if useprefix else "")

def process_folia(doc, outputdir, outputprefix=""):
    for sentence in doc.sentences():
        print("\tWriting " + outputprefix + sentence.id + '.alpino.xml',file=sys.stderr)
        with open(os.path.join(outputdir, outputprefix + sentence.id + '.alpino.xml'),'w',encoding='utf-8') as f:
            f.write(alpino_parse(sentence.text()))

def main():
    parser = argparse.ArgumentParser(description="Parse FoLiA documents with Alpino", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-E','--extension', type=str,help="", action='store',default="xml",required=False)
    parser.add_argument('-o','--outputdir', type=str,help="", action='store',default=".",required=False)
    parser.add_argument('--fileid', help="Use filename in ID (needed if FoLiA ID's are not unique)", action='store_true',required=False)
    parser.add_argument('inputfiles', nargs='+', help='Input file or directory')
    args = parser.parse_args()

    for filename in args.inputfiles:
        if os.path.isdir(filename):
            process_dir(filename, args.extension, args.outputdir, filename, args.fileid)
        else:
            print("Processing file " + filename,file=sys.stderr)
            doc = folia.Document(file=filename)
            process_folia(doc, args.outputdir)

if __name__ == '__main__':
    main()

