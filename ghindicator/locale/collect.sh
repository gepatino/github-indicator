#!/bin/bash

. config

xgettext --default-domain=$DOMAIN --output=$DOMAIN.pot ../*.py
