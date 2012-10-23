#!/usr/bin/env python
# -*- coding: utf-8 -*-
## auto last change for vim and Emacs: (whatever comes last)
## Latest change: Mon Mar 08 11:49:34 CET 2010
## Time-stamp: <2012-04-21 23:12:58 vk>
"""
analyze_artifacts_tagstore.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by Karl Voit <Karl.Voit@IST.TUGraz.at>
:license: GPL v2 or any later version
:bugreports: <Karl.Voit@IST.TUGraz.at>

See USAGE below for details!

FIXXME:
    * look for the string FIXXME to improve this script
    * encoding problems with tags containing German umlauts

"""

import logging    # logging
import sys        # flushing stdout
import os         # accessing file system
from optparse import OptionParser  # parsing command line options
import re         # RegEx
import codecs     # fixing UTF-8 issues

## for CSV
import csv

## debugging:   for setting a breakpoint:  pdb.set_trace()
import pdb

#counts the distinct words
from collections import defaultdict

## ======================================================================= ##
##                                                                         ##
##         You should NOT need to modify anything below this line!         ##
##                                                                         ##
## ======================================================================= ##

## example:   Winterurlaub%20ist%20Schiurlaub.pdf\tags="news,urlaub"
FILEENTRY_REGEX = re.compile("(.+)\\\\tags=(\")?(.+(,)?)+(\")?$")
## group 1 = itemname
## group 3 = string of tags, concatenated with ","


USAGE = "\n\
         %prog tagstore*.tgs\n\
\n\
This script reads in one or multiple store.tgs files of tagstore\n\
(probably renamed to something like \"TP42_store.tgs\") and calculates\n\
misc statistical data.\n\
Output will be written to CSV files.\n\
\n\
  :URL:        https://github.com/novoid/2011-04-tagstore-formal-experiment\n\
  :copyright:  (c) 2012 by Karl Voit <Karl.Voit@IST.TUGraz.at>\n\
  :license:    GPL v2 or any later version\n\
  :bugreports: <Karl.Voit@IST.TUGraz.at>\n\
\n\
Run %prog --help for usage hints\n"

parser = OptionParser(usage=USAGE)

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="do not output anything but just errors on console")


(options, args) = parser.parse_args()


class vk_FileNotFoundException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def handle_logging():
    """Log handling and configuration"""

    if options.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif options.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
    else:
        FORMAT = "%(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def error_exit(errorcode, text):
    """exits with return value of errorcode and prints to stderr"""

    sys.stdout.flush()
    logging.error(text + "\n")
    sys.exit(errorcode)


def guess_tp_number(string):
    """parses a string for occurrence of a number"""

    ## replacing all non-digits from the string and converting it to a integer
    digits = re.sub("\D", "", string)

    if not digits:
        error_exit(3, "ERROR: filename \"" + string + "\" contains no digit which " + \
                       "could lead to a TP number.\nPlease keep TP numbers in file names.")

    return int(digits)


def desanitize(string):
    """reverse sanitizing of strings"""

    ## FIXXME: maybe more characters are sanitized?
    return string.replace('%20', ' ')


def handle_filename(filename):
    """Processes one tagstore.tgs file and store item/tag information"""

    logging.debug("\n")
    logging.info("====> processing file [%s]" % filename)

    if not os.path.isfile(filename):
        error_exit(2, "ERROR: \"%s\" is not a file." % filename)

    tpnumber = guess_tp_number(filename)
    logging.info("I guess this is TP number %s" % str(tpnumber))

    tpdata = {'TPnum': tpnumber, 'items': []}  # initialize data structure for TP

    for line in codecs.open(filename, 'r', "utf-8"):
        components = FILEENTRY_REGEX.match(line.strip())
        if components:

            itemname = desanitize(components.group(1))  # fix sanitizing of space character

            logging.debug("---- match:    [%s]" % line.strip())
            logging.debug("  itemname: [%s]" % itemname)

            itemdata = {'name': itemname, 'tags': []}  # initialize data structure for item

            taglist = components.group(3).split(',')

            ## hack: correct doublequote character of last tag:
            if taglist[-1][-1:] == '"':
                taglist[-1] = taglist[-1][:-1]

            for tag in taglist:
                #logging.debug("  tag: [%s]" % tag)
                itemdata['tags'].append(desanitize(tag))

            tpdata['items'].append(itemdata)
            #logging.debug("finished parsing one item")
    #pdb.set_trace()
    logging.debug("finished parsing TP file \"%s\"" % filename)
    

    #pdb.set_trace()
    return tpdata


def traverse_dataset(dataset):
    """traverses the data structure of tpdata"""

    ## example dataset of one TP with 2 items with several tags each:
    ## [{'TPnum': 3, 'items': [
    ##                       {'name': 'Abschaltung Krsko.pdf', 'tags': ['kernkraft', 'technik']},
    ##                       {'name': '7 Fragen zu Atomkraft und Fukushima.pdf', 'tags': ['kernkraft', 'technik']},
    ##                       {'name': 'Allergietest.jpg', 'tags': ['gesundheit', 'bild']}
    ##                       ]}]

    logging.debug("=========== dataset DUMP =================")
    logging.debug("dataset has %s TPs" % str(len(dataset)))
    for tp in dataset:
        logging.debug("TP number %s has %s items" % (str(tp['TPnum']), str(len(tp['items']))))
        for item in tp['items']:
            logging.debug("  item \"%s\" has %s tags" % (item['name'], str(len(item['tags']))))
            for tag in item['tags']:
                logging.debug("    tag \"%s\" has length %s" % (tag, len(tag)))

#pdb.set_trace()
def sumtags(tags):
    #sum of all tags
    for tags in items['tags']:
	    tags = item['tags']
	    return



def uniquewords(count, words):
    #counts the words, w = occurs, word_count[w] = times
	word_count = defaultdict(int)
	for words in dataset['tags']:
	    word_count[w.lower()] +=1
	for words, count in word_count.iteritems():
	    return word, word_count[w]
		
def allitems(item):
    #sum of all items
    for item in dataset['items']:
	    item = str(len(tp['items']))


class csvexport():
    
    def statistics_tagstore_tag(tags, filename):
        
        list1=["average(tags/items)", "sum_all_tags", "sum_len(all_tags)"]
        list2=[str(len(item['tags']))/str(len(tp['items'])), str(len(item['tags'])), len(tag)]
        result_tagstore_tag_statistics = filename + "_tagstore_tag_statistics.csv"
        try:
            writer = csv.writer(open(result_tagstore_tag_statistics, "wb"))
        except:
            if error_exit(6, "ERROR: not able to create file"):
                return

        writer = csv.writer(open(result_tagstore_tag_statistics, "wb"), delimiter= ';', quoting=csv.QUOTE_NONE)
        writer.writerow(list1)
        writer = csv.writer(open(result_tagstore_tag_statistics,"a"), delimiter=';',quoting=csv.QUOTE_NONE)
        writer.writerow(list2) 
        print "CSV file " + result_tagstore_tag_statistics + " constructed! \n"
    
    def usage_tagstore_tag(w, word_count):
        list1=["unique_tag","#usage"]
        list2=[w, word_count]
        result_tagstore_tag_usage = filename + "_tagstore_tag_usage.csv"
        try:
            writer = csv.writer(open(result_tagstore_tag_usage, "wb"))
        except:
            if error_exit(7, "ERROR: not able to create file"):
                return

        writer = csv.writer(open(result_tagstore_tag_usage, "wb"), delimiter= ';', quoting=csv.QUOTE_NONE)
        writer.writerow(list1)
        writer = csv.writer(open(result_tagstore_tag_usage,"a"), delimiter=';',quoting=csv.QUOTE_NONE)
        writer.writerow(list2) 
        print "CSV file " + result_tagstore_tag_usage + " constructed! \n"
    
    def usage_tag_tagstore_allTP():
        list1=["unique_tag"]
        list2=[]
        result_ALLTP_tagstore_tag_usage = "ALLTP_tagstore_tag_usage.csv"
        try:
            writer = csv.writer(open(result_ALLTP_tagstore_tag_usage, "wb"))
        except:
            if error_exit(7, "ERROR: not able to create file"):
                return

        writer = csv.writer(open(result_ALLTP_tagstore_tag_usage, "wb"), delimiter= ';', quoting=csv.QUOTE_NONE)
        writer.writerow(list1)
        writer = csv.writer(open(result_ALLTP_tagstore_tag_usage,"a"), delimiter=';',quoting=csv.QUOTE_NONE)
        writer.writerow(list2) 
        print "CSV file " + result_ALLTP_tagstore_tag_usage + " constructed! \n"

    def usage_statistic_tagstore_allTP():
        list1=["item", "sum_of_tags", "sum_of_chars"]
        list2=[]
        result_ALLTP_tagstore_statistics = "ALLTP_tagstore_statistics.csv"
        try:
            writer = csv.writer(open(result_ALLTP_tagstore_statistics, "wb"))
        except:
            if error_exit(7, "ERROR: not able to create file"):
                return

        writer = csv.writer(open(result_ALLTP_tagstore_statistics, "wb"), delimiter= ';', quoting=csv.QUOTE_NONE)
        writer.writerow(list1)
        writer = csv.writer(open(result_ALLTP_tagstore_statistics,"a"), delimiter=';',quoting=csv.QUOTE_NONE)
        writer.writerow(list2) 
        print "CSV file " + result_ALLTP_tagstore_statistics + " constructed! \n"		


def main():
    """Main function [make pylint happy :)]"""

    print "                analyze_artifacts_tagstore.py\n"
    print "          (c) 2012 by Karl Voit <Karl.Voit@IST.TUGraz.at>"
    print "              GPL v2 or any later version\n"

    handle_logging()

    if len(args) < 1:
        parser.error("Please add at least one file name as argument")

    dataset = []  # initialize the dataset

    for filename in args:
        dataset.append(handle_filename(filename))

    logging.debug("finished parsing file")

    traverse_dataset(dataset)

    logging.info("finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################
# vim:foldmethod=indent expandtab ai ft=python tw=120 fileencoding=utf-8 shiftwidth=4
