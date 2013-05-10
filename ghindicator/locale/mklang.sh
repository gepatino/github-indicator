#!/bin/bash

if [ "" == "$1" ]
then
    echo "Indicate new language as first argument"
    exit 1 
fi

if [ -d $1 ]
then
    echo "The specified language already has it's directory"
    exit 1
fi

mkdir -p $1/LC_MESSAGES

for a in *.pot
do
    fname=`basename $a .pot`
    cp $a $1/$fname.po
done

