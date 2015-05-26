#!/usr/bin/env python3

# Conversiescript voor Groningse data voor CTVE project naar FoLiA

import sys
import os
import ucto #pylint: disable=import-error
from pynlpl.formats import folia

filename = sys.argv[1]

tmpfilename = filename.replace('.txt','')
foliafilename = filename.replace('.txt','') + '.folia.xml'

corrections = []
gaps=[]
correctionbuffer = ""
gapbuffer=""
incorrection = False
ingap = False

text = ""
with open(filename,'r',encoding='iso-8859-15') as f, open(tmpfilename,'w',encoding='utf-8') as f_out:
    for line in f:
        newline = ""
        for c in line:
            if c == '#':
                if incorrection:
                    incorrection = False
                    newline += "%C" + str(len(corrections)) + "%" #placeholder
                    corrections.append( tuple(correctionbuffer.split('~')) )
                else:
                    incorrection = True
                    correctionbuffer = ""
            elif c == "[":
                ingap = True
                gapbuffer = ""
            elif c == "]":
                if ingap:
                    ingap = False
                    newline += "%G" + str(len(gaps)) + "%" #placeholder
                    gaps.append(gapbuffer)
                else:
                    newline += c
            elif incorrection:
                correctionbuffer += c
            elif ingap:
                gapbuffer += c
            else:
                newline += c
        f_out.write(newline)

tokenizer = ucto.Tokenizer("/home/proycon/lamachine/etc/ucto/tokconfig-nl-withplaceholder",xmloutput=True)
tokenizer.tokenize(tmpfilename, foliafilename)
os.unlink(tmpfilename)

foliadoc = folia.Document(file=foliafilename)
foliadoc.declare(folia.AnnotationType.CORRECTION, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml", annotator="Sjors van Ooij", annotatortype=folia.AnnotatorType.AUTO)
foliadoc.declare(folia.AnnotationType.GAP, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/gaps.foliaset.xml", annotator="Sjors van Ooij", annotatortype=folia.AnnotatorType.AUTO)

#remove text-content on sentences (will contain placeholders and has no added value):
for sentence in foliadoc.sentences():
    for i, item in enumerate(sentence.data):
        if isinstance(item, folia.TextContent):
            del sentence.data[i]

for word in foliadoc.words():
    if word.cls == "PLACEHOLDER":
        doc = word.doc
        if str(word)[1] == "C":
            index = int(str(word)[2:-1])
            originaltext,newtext = corrections[index]
            if all( not c.isalnum() for c in newtext ):
                word.cls = "PUNCTUATION"
            elif newtext.isnumeric():
                word.cls = "NUMBER"
            else:
                word.cls = "WORD"

            if originaltext.lower() == newtext.lower():
                correction = word.correct(new=newtext,cls='capitalizationerror')
                correction.original().settext(originaltext)
            elif ' ' in originaltext and originaltext.replace(' ','') == newtext:
                original = folia.Original(doc, *[ folia.Word(doc, x,cls="WORD",generate_id_in=word.parent) for x in originaltext.split(' ') ])
                correction = folia.Correction(doc, original,folia.New(doc, folia.Word(doc, newtext,generate_id_in=word.parent)),cls='spliterror')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif ' ' in newtext and newtext.replace(' ','') == originaltext:
                new = folia.New(doc, *[ folia.Word(doc, x,cls="WORD",generate_id_in=word.parent) for x in newtext.split(' ') ])
                correction = folia.Correction(doc, new,folia.Original(doc, folia.Word(doc, originaltext,generate_id_in=word.parent)),cls='runonerror')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif originaltext == "" and all( not c.isalnum() for c in newtext ):
                correction = folia.Correction(doc, folia.Original(doc),folia.New(doc, folia.Word(doc, newtext,cls="PUNCTUATION",generate_id_in=word.parent)),cls='missingpunctuation')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif originaltext == "":
                #insertion
                correction = word.correct(new=newtext, cls='missingword')
                correction.original().data = []
            elif newtext == "":
                #deletion
                if not originaltext.isalnum():
                    correction = word.correct(new=[], cls='redundantpunctuation')
                else:
                    correction = word.correct(new=[], cls='redundantword')
            else:
                for i, item in enumerate(word.data):
                    if isinstance(item, folia.TextContent):
                        del word.data[i]
                word.append(folia.Correction,  folia.Original( doc, folia.TextContent(doc,originaltext)), folia.New(doc, folia.TextContent(doc,newtext)), cls="uncertain")

        elif str(word)[1] == "G":
            index = int(str(word)[2:-1])
            gapcontent = gaps[index]
            index = word.parent.getindex(word)
            if all( ( c == '$' for c in gapcontent) ):
                word.parent.data[index] = folia.Gap(doc, cls='cancelled')
            else:
                word.parent.data[index] = folia.Gap(doc,content=gapcontent, cls='cancelled')

foliadoc.save()






