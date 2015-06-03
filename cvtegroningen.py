#!/usr/bin/env python3

# Conversiescript voor Groningse data voor CTVE project naar FoLiA

import sys
import os
import re
import ucto #pylint: disable=import-error
from pynlpl.formats import folia #pylint: disable=import-error



# Changes with respect to original data:

# - Hyphenisation is undone and the linebreak is put prior to the hyphenised word
# - Crossed-out text inside corrections are ignored completely:  #typ[e]p~typ#
#    (crossed-out text outside of corrections are preserved as gaps, when
#    occuring in the middle of a word, they are preserved as t-gaps in an
#    additional t with class original.





def processdir(dirname,parseonly=False):
    for f in os.listdir(dirname):
        f = os.path.join(dirname,f)
        if f.endswith('.txt'):
            processfile(f,parseonly)
        elif os.path.isdir(f):
            processdir(f,parseonly)

def processfile(filename,parseonly=False):
    tmpfilename = filename.replace('.txt','')
    foliafilename = filename.replace('.txt','') + '.folia.xml'

    corrections = []
    gaps=[]
    inlinegaps=[]
    correctionbuffer = ""
    gapbuffer=""
    hyphbuffer = ""
    incorrection = False
    ingap = False
    mins = None
    words = None
    nospace = False
    hyph = False
    docid = os.path.basename(tmpfilename)
    score = None
    sentencebreak = False
    begin = 0
    skipchar = 0

    with open(filename,'r',encoding='iso-8859-15') as f, open(tmpfilename,'w',encoding='utf-8') as f_out:
        for linenum, line in enumerate(f):
            if hyphbuffer:
                line = hyphbuffer + line.lstrip()
                hyphbuffer = ""
            newline = ""
            strippedline = line.strip()
            if not strippedline:
                #empty line forces sentences break on next output
                sentencebreak = True
            if linenum == 0 and strippedline.find('score') != -1:
                tmpdocid = strippedline.split(' ')[0].strip()
                if tmpdocid[0] == 'T':
                    docid = tmpdocid
                else:
                    print("WARNING: DocID could not be read from " + filename +", first line has garbage",file=sys.stderr)
                score = strippedline.split(' ')[-1][:-1]
                continue
            if strippedline and strippedline[0] == '(' and strippedline[-1] == ')' and strippedline.find('min') != -1 and strippedline.find('words') != -1:
                fields = strippedline[1:-1].split(' ')
                mins = fields[0]
                words = fields[2]
                continue

            for i, c in enumerate(line):
                if skipchar:
                    skipchar = skipchar - 1
                    continue
                if c == '#':
                    if incorrection:
                        incorrection = False
                        if hyph:
                            newline += "%B%"
                        newline += "%C" + str(len(corrections)) + "%" #placeholder
                        try:
                            originaltext, newtext = correctionbuffer.split('~')
                        except ValueError:
                            print("i=",i," LINE=", line,file=sys.stderr)
                            raise Exception("Unable to split correctionbuffer in " + filename + ": " + correctionbuffer)
                        if hyph:
                            newtext = newtext.replace('-','')
                        corrections.append( (originaltext, newtext) )
                        if newtext in ('.','?'):
                            newline += " <utt> " #force new sentence
                    else:
                        incorrection = True
                        hyph = False
                        correctionbuffer = ""
                elif c == '-' and i < len(line) - 1 and line[i+1] == "\n":
                    if incorrection:
                        hyph = True
                    else:
                        hyphbuffer = ""
                        for j in range(i-1,0,-1):
                            if line[j].isalpha():
                                hyphbuffer = line[j] + hyphbuffer
                            else:
                                break
                        newline = newline[:-len(hyphbuffer)]
                    skipchar = 1
                    continue
                elif c == "[":
                    ingap = True
                    gapbuffer = ""
                    if i > 0:
                        nospace = (line[i-1] != " ")
                        begin = i-1
                    else:
                        nospace = False
                elif c == "]":
                    if ingap:
                        if nospace and i +1 < len(line) and line[i+1].isalnum():
                            #gap is in the middle of a word
                            ingap = False
                            left = ""
                            for j in range(begin,0,-1):
                                if line[j].isalpha():
                                    left = line[j] + left
                                else:
                                    break
                            newline = newline[:-len(left)]
                            right = ""
                            for j in range(i+1,len(line)):
                                if line[j].isalpha():
                                    right = right + line[j]
                                else:
                                    break
                            skipchar = len(right)
                            if left or right:
                                newline += "%I" + str(len(inlinegaps)) + "%" #placeholder
                                inlinegaps.append((left,gapbuffer,right))
                            else:
                                newline += "%G" + str(len(gaps)) + "%" #placeholder
                                gaps.append(gapbuffer)
                        else:
                            ingap = False
                            newline += "%G" + str(len(gaps)) + "%" #placeholder
                            gaps.append(gapbuffer)
                    else:
                        newline += c
                elif c == "\\" and i < len(line) - 1 and line[i+1] == "\\":
                    skipchar = 1
                    newline += "%C" + str(len(corrections)) + "%" #placeholder
                    corrections.append( ('','.') )
                    newline += " <utt> " #force new sentence
                    newline += " %H%" #placeholder triggering capitalization of next word
                elif incorrection and not ingap:
                    correctionbuffer += c
                elif ingap:
                    gapbuffer += c
                elif c != "\r":
                    newline += c
            if strippedline and newline and not ingap and not incorrection:
                if sentencebreak:
                    newline += "<utt>"
                    sentencebreak = False
                newline += "%B%"
            f_out.write(newline)


    print("docid: ", docid, file=sys.stderr)
    if parseonly:
        return
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

    dirname = os.path.basename(os.path.dirname(filename))
    print(filename,"--",dirname,file=sys.stderr)
    foliadoc.metadata['school'] = " ".join(dirname.split(' ')[:-2])
    foliadoc.metadata['class'] = dirname.split(' ')[-1]

    #remove text-content on paragraphs (will contain placeholders and has no added value):
    for paragraph in foliadoc.paragraphs():
        for i, item in enumerate(paragraph.data):
            if isinstance(item, folia.TextContent):
                del paragraph.data[i]

    #remove text-content on sentences (will contain placeholders and has no added value):
    for sentence in foliadoc.sentences():
        for i, item in enumerate(sentence.data):
            if isinstance(item, folia.TextContent):
                del sentence.data[i]

    for word in list(foliadoc.words()):
        if word.cls == "PLACEHOLDER":
            #print("Processing placeholder ", str(word),file=sys.stderr)
            doc = word.doc
            if str(word)[1] == "H":
                nextword = word.next(folia.Word)
                if nextword and str(nextword)[0] != '%':
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
                        cls='redundantpunctuation'
                    else:
                        cls='redundantword'
                    parent = word.parent
                    index = parent.getindex(word)
                    correction = folia.Correction(doc, folia.New(doc),folia.Original(doc, folia.Word(doc,originaltext,cls="WORD",generate_id_in=parent) ),cls=cls)
                    parent.data[index] = correction
                elif ' ' in originaltext or ' ' in newtext:
                    new = folia.New(doc, *[ folia.Word(doc, x,cls="WORD",generate_id_in=word.parent) for x in newtext.split(' ') ])
                    original = folia.Original(doc, *[ folia.Word(doc, x,cls="WORD",generate_id_in=word.parent) for x in originaltext.split(' ') ])
                    correction = folia.Correction(doc, new, original,cls='uncertain')
                    index = word.parent.getindex(word)
                    word.parent.data[index] = correction
                else:
                    for i, item in enumerate(word.data):
                        if isinstance(item, folia.TextContent):
                            del word.data[i]
                    word.append(folia.Correction,  folia.Original( doc, folia.TextContent(doc,originaltext)), folia.New(doc, folia.TextContent(doc,newtext)), cls="uncertain")

            elif str(word)[1] == "G":
                try:
                    index = int(str(word)[2:-1])
                except ValueError:
                    print("WORD=", str(word),file=sys.stderr)
                    raise
                gapcontent = gaps[index]
                index = word.parent.getindex(word)
                if all( ( c == '$' for c in gapcontent) ):
                    word.parent.data[index] = folia.Gap(doc, cls='cancelled')
                else:
                    word.parent.data[index] = folia.Gap(doc, folia.Content(doc, value=gapcontent), cls='cancelled')
            elif str(word)[1] == "I":
                index = int(str(word)[2:-1])
                left, gapcontent, right = inlinegaps[index]
                word.settext(left + right)
                gap = folia.TextMarkupGap(doc, gapcontent,cls='cancelled')
                word.add(folia.TextContent, left, gap, right, cls='original')
                word.cls = "WORD"
            elif str(word)[1] == "B":
                index = word.parent.getindex(word)
                if index == 0:
                    #add to end of previous sentence
                    prevsentence = word.parent.previous(folia.Sentence,None)
                    if prevsentence:
                        prevsentence.add(folia.Linebreak)
                        word.parent.remove(word)
                    else:
                        word.parent.data[index] = folia.Linebreak(doc)
                    if len(prevsentence) == 0: #remove empty sentence
                        prevsentence.parent.remove(prevsentence)
                else:
                    word.parent.data[index] = folia.Linebreak(doc)
            else:
                raise Exception("Can not resolve placeholder " + str(word))




    foliadoc.save()





if __name__ == '__main__':
    filename = sys.argv[1]
    if len(sys.argv) == 3 and sys.argv[2] == "parseonly":
        parseonly = True
    else:
        parseonly = False
    if os.path.isdir(filename):
        processdir(filename,parseonly)
    else:
        processfile(filename, parseonly)
