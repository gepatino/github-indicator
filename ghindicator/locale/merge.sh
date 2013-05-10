#!/bin/bash

. config

for lang in *
do
    if [ -d $lang ]
    then
        msgmerge --output-file=$lang/$DOMAIN.po $lang/$DOMAIN.po $DOMAIN.pot
    fi
done
