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

text = ""
with open(filename,'r',encoding='utf-8') as f, open(tmpfilename,'w',encoding='utf-8'):
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
        tmpfilename.write(newline)

tokenizer = ucto.Tokenizer(settingsfile="/home/proycon/lamachine/etc/ucto/tokconfig-nl-withplaceholder",xmloutput=True)
tokenizer.tokenize(tmpfilename, foliafilename)
os.unlink(tmpfilename)

foliadoc = folia.Document(file=foliafilename)
foliadoc.declare(folia.AnnotationType.CORRECTION, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml")
foliadoc.declare(folia.AnnotationType.GAPS, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/gaps.foliaset.xml")

for word in foliadoc.words():
    if word.cls == "PLACEHOLDER":
        doc = word.doc
        if str(word)[1] == "C":
            index = int(str(word)[2:-1])
            originaltext,newtext = corrections[index]
            if originaltext.lower() == newtext.lower():
                word.correct(original=originaltext, new=newtext,cls='capitalizationerror')
            elif ' ' in originaltext and originaltext.replace(' ','') == newtext:
                original = folia.Original(doc, *[ folia.Word(doc, x,cls="WORD") for x in originaltext.split(' ') ])
                correction = folia.Correction(doc, original,folia.New(folia.Word(doc, newtext)),cls='spliterror')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif ' ' in newtext and newtext.replace(' ','') == originaltext:
                new = folia.New(doc, *[ folia.Word(doc, x,cls="WORD") for x in newtext.split(' ') ])
                correction = folia.Correction(doc, new,folia.Original(folia.Word(doc, originaltext)),cls='runonerror')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif originaltext == "" and not newtext.alnum():
                correction = folia.Correction(folia.Original(doc),folia.New(doc, folia.Word(doc, newtext,cls="PUNCTUATION")),cls='missingpunctuation')
                index = word.parent.getindex(word)
                word.parent.data[index] = correction
            elif originaltext == "":
                #insertion
                correction = word.correct(new=newtext, cls='missingword')
                correction.original().data = []
            elif newtext == "":
                #deletion
                if not originaltext.alnum():
                    correction = word.correct(new=[], cls='redundantpunctuation')
                else:
                    correction = word.correct(new=[], cls='redundantword')
            else:
                word.correct(original=originaltext, new=newtext,cls="uncertain")


        elif str(word)[1] == "G":
            index = int(str(word)[2:-1])
            gapcontent = gaps[index]

foliadoc.save()






