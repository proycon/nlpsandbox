#!/bin/bash


source=$1
target=$2

sourcefilename=$(basename $source)
sourceext=${sourcefilename##*.}
sourcelang=${sourcefilename%.*}

targetfilename=$(basename $target)
targetext=${targetfilename##*.}
targetlang=${targetfilename%.*}

#Use plain2snt.out to convert your corpus into GIZA++ format:
plain2snt.out $source $target

mkcls -m2 -p ${source} -c50 -V ${sourcelang}.vcb.classes opt
mkcls -m2 -p ${target} -c50 -V ${targetlang}.vcb.classes opt

GIZA++ -S ${sourcelang}.vcb -T ${targetlang}.vcb -C "${sourcelang}_${targetlang}.snt" -p0 0.98 -o "${sourcelang}-${targetlang}"
