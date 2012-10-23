#/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import string
import codecs
import sys

words = []
#file = open(sys.argv[1], 'r')
file = codecs.open(sys.argv[1], 'r', 'utf-8')
#def trueline():
for line in file:

    if line.find("tags") > -1:
        left, right = line.split('\\', 1)
        tagside = right
        filename = left
        lefttag, tagwords = line.split('=')
        tags = tagwords.strip()
        pattern = re.sub(r'[\W]', '', tags)
        tag_chars = len(pattern)
        length = sum(len(pattern) for tags in tagwords)
        newver = tags.split(',')
        #print tags
        print "words:", len(newver)

        print "chars:", tag_chars

oneusertags = [ "foo", "bar", "eins zwei", "drei vier" ]


## FIXXME: Methoden zur Auswertung für einen User mit Ausgabe einer CSV-Zeile auf stdout (vorerst)

def generate_statistics_for_one_user(oneunsertags):
    ## FIXXME

# def analyze(tags):
#     wordcounts = map(len, tags)
#     return wordcounts
# for wordCount in analyze(tags):
#     print "sumWords", wordCounts
