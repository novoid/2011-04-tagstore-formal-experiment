#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2011-12-02 16:04:39 vk>
"""
Auswertung_Hintergrundbefragung.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Karl Voit <Karl.Voit@IST.TUGraz.at>
:license: GPL v2 or any later version
:bugreports: <Karl.Voit@IST.TUGraz.at>

See USAGE below for details!

Naming convention: see http://www.python.org/dev/peps/pep-0008/
Maintining states of lexer only in lexer object, not global variables!

FIXXME: open todos

"""

import logging   ## simple logging mechanism
import os        ## file system checks
import re        ## regular expressions
import fileinput ## read in files line by line
import time, sys
import codecs    ## e.g. UTF-8 handling
import csv
import math

import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict  ## for collecting things in integer dics

from optparse import OptionParser  ## parsing command line options

## debugging:   for setting a breakpoint:  pdb.set_trace()
import pdb

INVOCATION_TIME = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
PROG_VERSION_NUMBER = u"0.1"

EDUCATION_TRANSLATIONS = { u'Lehre':u'apprenticed', u'Matura':u'high school', \
                               u'Studium':u'graduated', u'Doktorat':u'PhD' }
SEX_TRANSLATIONS = { u'männlich':u'male', u'weiblich':u'female' }
YESNO_TRANSLATIONS = { u'ja':u'yes', u'nein':u'no' }





## ======================================================================= ##
##                                                                         ##
##         You should NOT need to modify anything below this line!         ##
##                                                                         ##
## ======================================================================= ##


USAGE = u"\n\
         " + sys.argv[0] + u"\n\
\n\
This script parses CSV files containing TP informations and generates \n\
statistics and graphics.\n\
\n\
Usage:  " + sys.argv[0] + u" <options>\n\
\n\
Example:\n\
     " + sys.argv[0] + u" -c Daten_Testpersonen_gefiltert.csv \n\
\n\
\n\
:copyright: (c) 2011 by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v2 or any later version\n\
:bugreports: <tools@Karl-Voit.at>\n\
:version: "+PROG_VERSION_NUMBER+"\n"


cmd_line_parser = OptionParser(usage=USAGE)

## for (future) command line argument for checking only - if necessary)
# cmd_line_parser.add_option("-c", "--check", dest="checkonly",
#                   help="check the input file(s) only and print out errors", metavar="CHECKONLY")

cmd_line_parser.add_option("-c", "--csvfile", dest="csvfilename",
                  help="CSV file of TP", metavar="FILE")

cmd_line_parser.add_option("--sexpie", dest="sexpie", action="store_true",
                  help="pie graph of TP sex")
cmd_line_parser.add_option("--education", dest="education", action="store_true",
                  help="pie graph of TP education")
cmd_line_parser.add_option("--os", dest="os", action="store_true",
                  help="pie graph of TP operating system (messy!)")
cmd_line_parser.add_option("--filebrowser", dest="filebrowser", action="store_true",
                  help="pie graph of TP filebrowser (messy!)")
cmd_line_parser.add_option("--taggingknown", dest="taggingknown", action="store_true",
                  help="pie graph showing which TP known tagging")
cmd_line_parser.add_option("--taggingusing", dest="taggingusing", action="store_true",
                  help="pie graph showing which TP uses tagging")


cmd_line_parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

cmd_line_parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="do not output anything but just errors on console")
             
## handle command line options:
(options, args) = cmd_line_parser.parse_args()


## general purpose methods: ---------------------------------------------


class vk_FileNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def handle_logging():
    """Setting up log handling and configuration."""

    if options.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif options.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
    else:
        FORMAT = "%(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def preprocess_csv_value(csvvalue):
    """pre-processes the values read in from CSV file"""

    value = unicode(csvvalue.strip('"'))
    return value


def parse_csvfile(filename):
    """parses an csv file and generates orgmode entries"""

    basename = os.path.basename(filename).strip()
    logging.debug( "--------------------------------------------")
    logging.debug("processing file \""+ filename + "\" with basename \""+ basename + "\"")
    firstline = True
    TPdata = []  ## TP-list of data-lists

    ## please do *not* use csvreader here since it is not able to handle UTF-8/latin-1!
    inputfile = codecs.open(filename, 'rb', 'utf-8')
    for line in inputfile:

        TPnum = TPsex = TPeducation = None  ## init things to prevent working on old values

        if firstline:
            logging.debug("ignoring first line since it is CSV header")
            firstline = False
            continue

        row = line.split(";")
        #logging.debug("--------------------------------------------------------")
        #logging.debug("processing row: " + unicode(str(row)) )

        ## direct data:
        try:
            TPnum = preprocess_csv_value(row[0])
            TPsex = preprocess_csv_value(row[1])
            TPeducation = preprocess_csv_value(row[4])
            TPcomputerusageY = preprocess_csv_value(row[6])
            TPos = preprocess_csv_value(row[11])
            TPfilebrowser = preprocess_csv_value(row[12])
            TPtaggingknown = preprocess_csv_value(row[19])
            TPtaggingusing = preprocess_csv_value(row[21])
        except UnicodeDecodeError as detail:  ## FIXXME: ValueError oder so?
            logging.error("Encoding error: ")
            print detail
            logging.error("corresponding line is: [" + unicode(str(row)) + "]")
            sys.exit(4)

        if TPnum == "PT":
            logging.debug("skipping pilot test user")
            continue

        logging.debug("TPnum [%s]  TPsex [%s]  TPeducation [%s]" % (TPnum, TPsex, TPeducation) )

        TPdata.append( {"num":TPnum, "sex":TPsex, "education":TPeducation, "os":TPos, \
                            "filebrowser":TPfilebrowser, "taggingknown":TPtaggingknown, \
                            "taggingusing":TPtaggingusing, "computerusageY":TPcomputerusageY} )

    return TPdata



def translate_labels(labels, translationdict):
    """translate education labels from German to English using a given dictionary"""

    en_labels = []

    for de_label in labels:
        try:
            en_labels.append(translationdict[de_label])
        except KeyError:
            logging.error("English translation for [%s] is not known!", de_label )
            sys.exit(6)

    return en_labels



def add_sum_to_labels(values, labels):
    """add the sum to the labels"""

    return [u"{} ({})".format(i, j) for i, j in zip(labels, values)]



## def OLD_generate_statistic_sex(TPdata):
##     """generates the statistics about the sex of the TP"""
## 
##     logging.debug("number of TPs [%s]", str(len(TPdata)) )
## 
##     num_males = num_females = 0
## 
##     for TP in TPdata:
##         if TP['sex'] == u"männlich":
##             num_males += 1
##         elif TP['sex'] == u"weiblich":
##             num_females += 1
##         else:
##             logging.error("TP [%s] is neither male nor female!", str(TP['num']) )
##             sys.exit(5)
## 
##     logging.debug("number of males [%s] females [%s]" % ( str(num_males), str(num_females) ) )
## 
##     ## I got the numbers. lets draw the pie chart
## 
##     fig1 = plt.figure(figsize=(8,8)) ## makes sure that there is no squeezing of the round pie
##     plt.axis('equal')
## 
##     values = [num_males, num_females] 
##     labels = ["males", "females"]
## 
##     labels = add_sum_to_labels(values, labels)
##     plt.pie(values, explode=None, \
##                 labels=labels, colors=None, autopct=None, pctdistance=0, \
##                 shadow=False, labeldistance=1.1, hold=None)
## 
##     plt.show()




## def OLD_generate_statistic_education(TPdata):
##     """generates the statistics about the education of the TP"""
## 
##     logging.debug("number of TPs [%s]", str(len(TPdata)) )
## 
##     educations = defaultdict(int)  # empty dictionary
## 
##     for TP in TPdata:
##         educations[TP['education']] += 1
## 
##     logging.debug("educations: [%s]", str(educations) )
## 
##     fig1 = plt.figure(figsize=(8,8)) ## makes sure that there is no squeezing of the round pie
##     #ax = plt.axes([0.1, 0.1, 0.8, 0.8])
##     plt.axis('equal')
## 
##     values = [value for key, value in educations.items()]
##     labels = educations.keys()
## 
##     labels = translate_labels(labels, EDUCATION_TRANSLATIONS)
##     labels = add_sum_to_labels(values, labels)
## 
##     plt.pie(values, explode=None, \
##                 labels=labels, colors=None, autopct=None, pctdistance=0, \
##                 shadow=False, labeldistance=1.1, hold=None)
## 
##     plt.show()



def generate_piechart(TPdata, key, dictionary):
    """generates a pie chart about a key in the dataset using translation dictionary"""

    counts = defaultdict(int)  # empty dictionary

    for TP in TPdata:
        counts[TP[key]] += 1

    logging.debug("extracted counts: [%s]", str(counts) )

    fig1 = plt.figure(figsize=(8,8)) ## makes sure that there is no squeezing of the round pie
    plt.axis('equal')

    values = [value for key, value in counts.items()]
    labels = counts.keys()

    if dictionary:
        labels = translate_labels(labels, dictionary)

    labels = add_sum_to_labels(values, labels)

    plt.pie(values, explode=None, \
                labels=labels, colors=None, autopct=None, pctdistance=0, \
                shadow=False, labeldistance=1.1, hold=None)

    plt.show()




def NOTWORKING_generate_barchart(TPdata, key):
    """generates a bar graph about a key in the dataset"""

    ## (complex) example:
    ## http://matplotlib.sourceforge.net/examples/pylab_examples/scatter_hist.html
    ## only chart on top is interesting here!

    counts = defaultdict(int)  # empty dictionary

    for TP in TPdata:
        counts[TP[key]] += 1

    logging.debug("extracted counts: [%s]", str(counts) )

    #fig1 = plt.figure(figsize=(8,8)) ## makes sure that there is no squeezing of the round pie
    plt.axis('equal')

    values = [value for key, value in counts.items()].sort()

    logging.debug("values [%s]", str(values) )
    

    #labels = counts.keys()

    #labels = add_sum_to_labels(values, labels)

    xvalues = range(min(values), max(values))

    n, bins, patches = plt.hist(xvalues, values, normed=1, histtype='bar', rwidth=0.8)
    #plt.pie(values, explode=None, \
    #            labels=labels, colors=None, autopct=None, pctdistance=0, \
    #            shadow=False, labeldistance=1.1, hold=None)

    plt.show()




def main():
    """Main function"""

    (options, args) = cmd_line_parser.parse_args()

    handle_logging()

    if not options.csvfilename:
        parser.error("Please provide an input file!")

    if not os.path.isfile(options.csvfilename):
    	print USAGE
    	logging.error("\n\nThe argument interpreted as an input file \"" + str(options.csvfilename) + \
                          "\" is not an normal file!\n")
        sys.exit(2)

#    logging.debug("found arguments: " + str(args))

    TP_data = parse_csvfile(options.csvfilename)

    if options.sexpie:
        generate_piechart(TP_data, u'sex', SEX_TRANSLATIONS)
    if options.education:
        generate_piechart(TP_data, u'education', EDUCATION_TRANSLATIONS)
    if options.os:
        generate_piechart(TP_data, u'os', None)
    if options.filebrowser:
        generate_piechart(TP_data, u'filebrowser', None)
    if options.taggingknown:
        generate_piechart(TP_data, u'taggingknown', YESNO_TRANSLATIONS)
    if options.taggingusing:
        generate_piechart(TP_data, u'taggingusing', YESNO_TRANSLATIONS)
#    if options.:
#    generate_barchart(TP_data, u'computerusageY')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################
# vim:foldmethod=indent expandtab ai ft=python tw=120 fileencoding=utf-8 shiftwidth=4
