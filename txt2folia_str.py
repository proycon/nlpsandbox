#!/usr/bin/env python3


from __future__ import print_function, unicode_literals, division, absolute_import

import sys
from pynlpl.formats import folia

def processbuffer(text, buffer):
    if buffer:
        paragraph = text.append(folia.Paragraph, buffer )
        substrings = buffer.split(' ')
        offset = 0
        for substring in substrings:
            paragraph.append(folia.String, folia.TextContent(paragraph.doc, substring, offset=offset) )
            offset += len(substring) + 1
        buffer = ""

if __name__ == '__main__':
    try:
        docid = sys.argv[2]
    except:
        docid = "untitled"

    doc = folia.Document(id=docid)
    text = doc.append(folia.Text)

    filename = sys.argv[1]

    buffer = ""
    linenum = 0
    with open(filename,'r',encoding='utf-8') as f:
        for line in f:
            linenum += 1
            line = line.strip("\n\r ")
            if not line: #paragraph boundary
                print(linenum,file=sys.stderr)
                processbuffer(text, buffer)
            else:
                if buffer: buffer += " "
                buffer += line
        print(linenum,file=sys.stderr)
        processbuffer(text,buffer)

    outfilename = filename.replace('.txt','') + ".folia.xml"
    doc.save(outfilename)

