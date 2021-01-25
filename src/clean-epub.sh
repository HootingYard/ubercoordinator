#!/bin/sh
# Build an empty EPUB directory tree

EPUB=$1
TEMPLATES=$2

# make EPUB directories, if they are not there
mkdir -p "$EPUB"
mkdir -p "$EPUB"/META-INF
mkdir -p "$EPUB"/OEBPS/Text
mkdir -p "$EPUB"/OEBPS/Images
mkdir -p "$EPUB"/OEBPS/Styles
mkdir -p "$EPUB"/OEBPS/Fonts

# remove existing files, if they are there
rm -f "$EPUB"/OEBPS/Text/*
rm -f "$EPUB"/OEBPS/Images/*
rm -f "$EPUB"/OEBPS/Styles/*
rm -f "$EPUB"/OEBPS/Fonts/*

# copy in EPUB identification files
cp "$TEMPLATES"/XML/mimetype "$EPUB"/
cp "$TEMPLATES"/XML/container.xml "$EPUB"/META-INF/
