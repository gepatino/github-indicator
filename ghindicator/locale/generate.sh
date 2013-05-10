#!/bin/bash

. config

for lang in *
do
    if [ -d $lang ]
    then
        msgfmt --output-file=$lang/LC_MESSAGES/$DOMAIN.mo $lang/$DOMAIN.po
    fi
done
