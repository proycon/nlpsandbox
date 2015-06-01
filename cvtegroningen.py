#!/usr/bin/env python3

# Conversiescript voor Groningse data voor CTVE project naar FoLiA

import sys
import os
import re
import ucto #pylint: disable=import-error
from pynlpl.formats import folia #pylint: disable=import-error

filename = sys.argv[1]
if os.path.isdir(filename):
    processdir(filename)
else:
    processfile(filename)

def processdir(dirname):
    for f in os.listdir(dirname):
        f = os.path.join(dirname,f)
        if f.endswith('.txt'):
            processfile(f)
        elif os.isdir(f):
            processdir(f)

def processfile(filename):
    tmpfilename = filename.replace('.txt','')
    foliafilename = filename.replace('.txt','') + '.folia.xml'

    corrections = []
    gaps=[]
    inlinegaps=[]
    correctionbuffer = ""
    gapbuffer=""
    incorrection = False
    ingap = False
    mins = None
    words = None
    nospace = False
    docid = os.path.basename(tmpfilename)
    score = None
    begin = 0
    skipchar = 0

    with open(filename,'r',encoding='iso-8859-15') as f, open(tmpfilename,'w',encoding='utf-8') as f_out:
        for linenum, line in enumerate(f):
            newline = ""
            if linenum == 0:
                m =  re.match(r"([%w%d_]+) \(score (%d+)\)", line)
                if m:
                    docid = m.group(1)
                    score = m.group(2)
            m =  re.match("(%d+) min; (%d+) words)", line)
            if m:
                mins = m.group(1)
                words = m.group(2)
            else:
                for i, c in enumerate(line):
                    if skipchar:
                        skipchar = skipchar - 1
                        continue
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
                        if i > 0:
                            nospace = (c[i-1] == " ")
                            begin = i-1
                        else:
                            nospace = False
                    elif c == "]":
                        if ingap:
                            if nospace and i +1 < len(line) and c[i+1].isalnum():
                                #gap is in the middle of a word
                                ingap = False
                                newline += "%I" + str(len(inlinegaps)) + "%" #placeholder
                                left = ""
                                for j in range(begin,0,-1):
                                    if line[j].isalpha():
                                        left = line[j] + left
                                right = ""
                                for j in range(i+1,len(line)):
                                    if line[j].isalpha():
                                        right = right + line[j]
                                inlinegaps.append((line,gapbuffer,right))
                            else:
                                ingap = False
                                newline += "%G" + str(len(gaps)) + "%" #placeholder
                                gaps.append(gapbuffer)
                        else:
                            newline += c
                    elif c == "\\" and i < len(line) - 1 and c[i+1] == "\\":
                        skipchar = 1
                        newline += "%C" + str(len(corrections)) + "%" #placeholder
                        corrections.append( ('','.') )
                        newline += " %H%" #placeholder triggering capitalization of next word
                    elif incorrection:
                        correctionbuffer += c
                    elif ingap:
                        gapbuffer += c
                    else:
                        newline += c
                newline += "%B%"
                f_out.write(newline)

    tokenizer = ucto.Tokenizer("/home/proycon/lamachine/etc/ucto/tokconfig-nl-withplaceholder",xmloutput=True,docid=docid)
    tokenizer.tokenize(tmpfilename, foliafilename)
    os.unlink(tmpfilename)

    foliadoc = folia.Document(file=foliafilename)
    foliadoc.declare(folia.AnnotationType.CORRECTION, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml", annotator="Sjors van Ooij", annotatortype=folia.AnnotatorType.AUTO)
    foliadoc.declare(folia.AnnotationType.GAP, "https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/gaps.foliaset.xml", annotator="Sjors van Ooij", annotatortype=folia.AnnotatorType.AUTO)

    if words is not None:
        foliadoc.metadata['words'] = words
    if mins is not None:
        foliadoc.metadata['annotationtime'] = mins
    if score is not None:
        foliadoc.metadata['score'] = score
    foliadoc.metadata['school'] = " ".join(os.path.basename(os.path.dirname(tmpfilename)).split(' ')[:-2])
    foliadoc.metadata['class'] = os.path.basename(os.path.dirname(tmpfilename)).split(' ')[-1]

    #remove text-content on sentences (will contain placeholders and has no added value):
    for sentence in foliadoc.sentences():
        for i, item in enumerate(sentence.data):
            if isinstance(item, folia.TextContent):
                del sentence.data[i]

    for word in foliadoc.words():
        if word.cls == "PLACEHOLDER":
            doc = word.doc
            if str(word)[1] == "H":
                nextword = word.next(folia.Word)
                if nextword:
                    originaltext = str(nextword)
                    newtext = str(nextword)[0].upper() + str(nextword)[1:]
                    correction = nextword.correct(new=newtext,cls='capitalizationerror')
                    correction.original().settext(originaltext)
                word.parent.remove(word)
            elif str(word)[1] == "C":
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
            elif str(word)[1] == "I":
                index = int(str(word)[2:-1])
                left, gapcontent, right = inlinegaps[index]
            elif str(word)[1] == "B":
                index = word.parent.getindex(word)
                word.parent.data[index] = folia.Linebreak(doc)




    foliadoc.save()






