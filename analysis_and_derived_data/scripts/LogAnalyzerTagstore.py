#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2011-07-21 18:21:20 vk>
"""
LogAnalyser.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Karl Voit <Karl.Voit@IST.TUGraz.at>
:license: GPL v2 or any later version
:bugreports: <Karl.Voit@IST.TUGraz.at>

See USAGE below for details!

Naming convention: see http://www.python.org/dev/peps/pep-0008/
Maintining states of lexer only in lexer object, not global variables!

from: http://pythonsource.com/open-source/parser-generators I found:
ply:  http://www.dabeaz.com/ply/
      http://www.dabeaz.com/ply/ply.html <- good source of information

FIXXME: open todos
    [x] vk: move lexer to class
      * see: http://www.dabeaz.com/ply/ply.html 4.14 "The module option can also be..."
    [x] vk: move lexer-variables to newly generated lexer-class: (refacturing)
      [x] seconds
      [x] numerrors
    [x] vk: create syntaxer
    [x] expand lexer with all tokens for task filing_tagstore (not only reduced set of it)
    [ ] create different parsers for other tasks: (re-use code as much as possible!)
      [ ] filing_folders
      [ ] refinding_tagstore AND refinding_folders (same parser)

"""

import logging   ## simple logging mechanism
import os        ## file system checks
import re        ## regular expressions
import fileinput ## read in files line by line
import csv
import math

from optparse import OptionParser  ## parsing command line options
import ply.lex as lex              ## lexical analysis
import ply.yacc as yacc            ## syntactical analysis
from copy import deepcopy

## debugging:   for setting a breakpoint:  pdb.set_trace()
#import pdb




## ======================================================================= ##
##                                                                         ##
##         You should NOT need to modify anything below this line!         ##
##                                                                         ##
## ======================================================================= ##



USAGE = "\n\
         %prog FIXXME\n\
\n\
FIXXME\n\
\n\
\n\
  :copyright:  (c) 2011 by Karl Voit <Karl.Voit@IST.TUGraz.at>\n\
  :license:    GPL v2 or any later version\n\
  :bugreports: <Karl.Voit@IST.TUGraz.at>\n\
\n\
\n\
Run %prog --help for usage hints\n"


cmd_line_parser = OptionParser(usage=USAGE)

## for (future) command line argument for checking only - if necessary)
# cmd_line_parser.add_option("-c", "--check", dest="checkonly",
#                   help="check the input file(s) only and print out errors", metavar="CHECKONLY")

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



class GenericParser(object):
    """This is a generic parser object.

    Here you can find all methods that parsing objects share.

    """

    ## switch to set of current tokens:
    tokens = ()

    ## holds the absolute time position in seconds:
    _seconds = -1

    ## holds the number of errors so far:
    _numerrors = 0

    ## holds the name of the file to parse:
    _filename = ""

    ## holds the current number of line of the input file:
    _linenumber = 1

    ## if True, do not parse but lex only
    _lexeronly = False
    
    ## test a state variable:
    _overallTime = 0
    
        ## test a state variable:
    _stateFileMGT = 0
    
        ## test a state variable:
    _stateTagging = 0
    
    _numOfTd = 0
    
    _numOfTp = 0
    
    _numOfTc = 0
    
    _tagsPerItem = 0
    
    _sumOfTags = 0
    
    _numOfTags = 0
    
    _numOfItems = 0
    
    _sumOfDistractions = 0
    
    _sumOfDistractionsA = 0
    
    _TaggingBeginnTimestamps = []
    
    _TaggingEndTimestamps = []
    
    _DistrBeginnTimestamps = []
    
    _DistrEndTimestamps = []
    
    _TaggingDistractions = 0
    
    _tempIBVar = 0 

    _FacilitatorTime = 0
    
    _TPInspectionTime = 0
    
    _FacilitatorTime = 0
    
    _CommentaryTime = 0
    
    _list1 = []
        
    _list2 = []
        
    _list3 = []
        
    _list4 = []
        
    _list5 = []
        
    _list6 = []
        
    _nrOfAssignedTags = []
    
    _ListOfTAsAndM2Ts = []
    
    _TimesForTaggingPerItem = []
    
    _ListOfEOTs = []
    
    _numOfM2Ts = 0

    def __init__(self, filenameargument, **kw):

        logging.info("Parsing file \"" + str(filenameargument) + "\"")

        ## this block is magic from calc.py example I do not understand (Voit)
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule


        # Build the lexer and parser
        lex.lex(module=self, debug=0)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

        ## store in lexer object
        logging.debug("initializing seconds to -1")
        self._seconds = -1
        logging.debug("initializing numerrors to 0")
        self._numerrors = 0
        logging.debug("initializing filename to ["+str(filenameargument) + "]")
        self._filename = str(filenameargument)

    def run(self):
        """Running the parser."""

        logging.debug("running parser with filename: [" + self._filename + "]")

        if self._lexeronly:
            logging.debug("doing *ONLY* lexical analysis, skipping syntactical analysis")
            ## debug output of lexical analysis: (FIXXME: replace with yacc parsing)
            for line in fileinput.input([self._filename]):
    
                logging.info("     processing line: [" + line.strip() + "]")
                
                ## Give the lexer some input
                lex.input(line)
                
                # Tokenize
                while True:
                    token = lex.token()
                    if not token: break      # No more input
                    logging.debug(str(token))

        else:
            yacc.parse(open(self._filename).read())
    
        ## report number of errors
        if self._numerrors>0:
            logging.critical("-> " + str(self._numerrors) + " ERRORS found while parsing " + self._filename)
        else:
            logging.info("no errors found while parsing " + self._filename)
    

    def find_column(self, input, token):
        """Compute the number of column for the token in the input string."""
        last_cr = input.rfind('\n',0,token.lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (token.lexpos - last_cr) + 1
        return column
    
    def get_min_sec_string_from_seconds(self, string):
        """Return a string containing the format MM:SS from the input string containing seconds."""
        try:
            minutes = int(int(string) / 60)
            seconds = int(string) % 60
        except ValueError:
            logging.critical("get_min_sec_string_from_seconds: the string \""+ str(string) + \
                                 "\" could not be parsed as a value")
            os.sys.exit(3)
    
        return str(minutes) + ":" + str(str(seconds).zfill(2))
    
    def get_position_info(self, token):
        """Return string with positional information of a token."""
        return "(line " + str(self._linenumber) + \
            ", position " + str(self.find_column(token.lexer.lexdata, token)) + \
            ", token nr. "+ str(token.lexpos) + \
            ", " + self.get_min_sec_string_from_seconds(self._seconds) + \
            ")"


class FilingTagstoreParser(GenericParser):
    """Provides a parser for the task »filing in tagstore«."""

    ## moving parser into class:
    ## http://groups.google.com/group/ply-hack/browse_thread/thread/b15780f8950f9d2d/7fe1667d067d32c7?lnk=gst&q=class#7fe1667d067d32c7

    ## reserved words for task "filing in tagstore":
    reserved = {
        'sott' : 'STARTTAGGINGTASK',
        'eott' : 'ENDTAGGINGTASK',
        'ib'   : 'BEGININSPECTION',
        'ie'   : 'ENDINSPECTION',
        'cf'   : 'BEGINCOMMENTFACILITATOR',
        'ct'   : 'BEGINCOMMENTTP',
        'cl'   : 'BEGINCOMMENTLOGGER',
        'ce'   : 'ENDCOMMENT',
        'fb'   : 'BEGINFACILITATOR',
        'fe'   : 'ENDFACILITATOR',
        'm2t'  : 'MOVEFILETOTAGSTOREDRIVE',
        'ta'   : 'ASSIGNTAGS',
        'tp'   : 'TAGPROPOSED',
        'td'   : 'TAGDEFAULT',
        'tc'   : 'TAGCOMPLETION',
        'eot'  : 'ENDOFTAGGING'
    }
    
    ## List of token names for task "filing in tagstore":
    tokens = list(reserved.values()) + [
        'TIMESTAMP',
        'WORDS',
        'WORD',
        'NUMBER'
    ]
    
    ## ignore spaces and tabs:
    t_ignore = " \t"

    def t_TIMESTAMP(self, t):
        ## complex timestamps starting with one or two digit minutes
        r'(\d)?(\d)?(:)?(\d)?\d:\d\d' ## matches one, two or three digits followed by colon and two digits
        try:
            components = t.value.split(':')

            try:
                if components[2]:
                    t.value = str(int(components[0])*60*60 + int(components[1])*60 + int(components[2])) 
            except:
                t.value = str(int(components[0])*60 + int(components[1])) 
            ## re-calculate mm:ss into seconds (normalization)
            ####t.value = str(int(components[0])*60 + int(components[1])) 
            #logging.debug("converted \"" + str(components) + "\" into \"" + str(t.value) + \
            #                  "\" seconds " + self.get_position_info(t))
        except ValueError:
            logging.critical("Error in converting timestamp \"" + (t.value) + \
                                 "\" into integers and seconds " + self.get_position_info(t))
            sys.os.exit(4)
    
        if int(t.value) < int(self._seconds):
            logging.critical("Error in timestamp \"" + self.get_min_sec_string_from_seconds(t.value) + \
                                 "\": it is before last timestamp (which was " + \
                                 self.get_min_sec_string_from_seconds(self._seconds) + ") " + \
                                 self.get_position_info(t))
            self._numerrors += 1
    
        ## set lexer time to current number of seconds
        self._seconds=t.value
        return t
    
    def t_NUMBER(self, t):
        ## matches numbers
        r'\d+'
        t.value = int(t.value)    
        return t
    
    def t_WORDS(self, t):
        ## complex string havin multiple words sourrounded by double quotes
        r'".*"'
        t.type = self.reserved.get(t.value,'WORDS')    # Check for reserved words
        #logging.debug("found " + str(t.type) + " \"" + t.value + "\" " + get_position_info(t)) 
        return t
    
    def t_WORD(self, t):
        ## string containing of one word (without double quotes)
        r'\w+'
        t.type = self.reserved.get(t.value,'WORD')    # Check for reserved words
        #logging.debug("found " + str(t.type) + " \"" + t.value + "\" " + get_position_info(t)) 
        return t
    
    def t_ignore_COMMENT(self, t):
        ## matches a comment line starting with sharp-character
        r'\#.*'
        logging.debug("found comment \"" + str(t.value) + "\"")
        pass ## ignore comment content
    
    def t_newline(self, t):
        ## match newlines to track line numbers
        r'\n+'
        self._linenumber += len(t.value)
    
    def t_error(self, t):
        ## error handling rule
        self._numerrors += 1
        print "Illegal character '%s'" % t.value[0] + " at linenumber: " + str(self._linenumber)
        t.lexer.skip(1)
    

    ## -------------------------------------
    ## end of lexer, start of syntaxer
    ## -------------------------------------
    
    

    def p_expression_task_tagstore_storage(self, p):
        ## the whole task from sott until eott
        '''
        tagstore_storage_task : TIMESTAMP STARTTAGGINGTASK filemgt
        '''
        
        # need to sort list of tagging timestamps, because it was mixed by parser
        self._DistrBeginnTimestamps.sort()
        self._DistrEndTimestamps.sort()
        self._TaggingBeginnTimestamps.sort()

        
        # calculate overall distractions
        for u, v in zip(self._DistrBeginnTimestamps, self._DistrEndTimestamps):
            difference = v-u
            if self._sumOfDistractions == 0:
                self._sumOfDistractions = difference
            else:
                self._sumOfDistractions += difference
        

        if p[2] == "sott":
            # subtract begin time from end time to calculate overall time
            self._overallTime -= int(p[1])
            
            # check if timestamps in distraction-list occure in tagging-list
            # if they do, then this is obviously an tagging distraction
            for x, y in [(x,y) for x in zip(self._DistrBeginnTimestamps,self._DistrEndTimestamps) for y in zip(self._TaggingBeginnTimestamps,self._TaggingEndTimestamps)]:
                if x[0] >= y[0] and x[0]<= y[1]:
                    time = int(x[1]) - int(x[0])
                    self._TaggingDistractions += time
            
            # calculate overall time without distractions
            overallTimeWithoutDistr = self._overallTime - self._sumOfDistractions
            # calculate net tagging time by subtraction tagging distractions
            teggingWithoutDistr = self._stateTagging - self._TaggingDistractions
            # FileManagement time is calculated by subtracting tagging time of overall time 
            FMGTOverall = self._overallTime - self._stateTagging
            # The FileManagement net time is: net overall time - net tagging time
            FMGTWithoutDistr = (overallTimeWithoutDistr - teggingWithoutDistr)
            # calculate assigned tags per tagged files
            avgTagsPerItem = self._numOfTags/float(self._numOfItems)
            
            FMGTDistractions = self._sumOfDistractions - self._TaggingDistractions
            
            
            print "\n### Overall Time:                 " + str(self._overallTime)
            print   "### Overall Time without distr.:  " + str(overallTimeWithoutDistr)
            print "\n### Tagging overall:              " + str(self._stateTagging)
            print   "### Tagging without distractions: " + str(teggingWithoutDistr)
            print "\n### FileMGT overall:              " + str(FMGTOverall)
            print   "### FileMGT without distractions: " + str(FMGTWithoutDistr)
            print "\n### Number of TD:                 " + str(self._numOfTd)
            print   "### Number of TP:                 " + str(self._numOfTp)
            print   "### Number of TC:                 " + str(self._numOfTc)
            print   "### Average Tags/Item:            " + str(avgTagsPerItem)
            print   "### Sum of tags:                  " + str(self._numOfTags)
            
            
            print "\n### Sum of distractions:          " + str(self._sumOfDistractions)
            print   "### Tagging distractions:         " + str(self._TaggingDistractions)
            print   "### FMGT distractions:            " + str(FMGTDistractions)
            
            
            ## calculate distraction split
            
            self._list1.sort()
            self._list2.sort()
            self._list3.sort()
            self._list4.sort()
            self._list5.sort()
            self._list6.sort()
            
        # calculate Testperson inspection time
        for a, b in zip(self._list1, self._list2):
            #print u, v
            difference1 = b - a
            if self._TPInspectionTime == 0:
                self._TPInspectionTime = difference1
            else:
                self._TPInspectionTime += difference1
        
        # calculate Facilitator time        
        for c, d in zip(self._list3, self._list4):
            #print u, v
            difference2 = d - c
            if self._FacilitatorTime == 0:
                self._FacilitatorTime = difference2
            else:
                self._FacilitatorTime += difference2
        
        # calculate commentary time
        for e, f in zip(self._list5, self._list6):
            #print u, v
            difference3 = f - e
            if self._CommentaryTime == 0:
                self._CommentaryTime = difference3
            else:
                self._CommentaryTime += difference3
            
            
            
        print "\n"
        print "Distraction time split:"
        print "### Testperson Inspection time:   " + str(self._TPInspectionTime)
        print "### Facilitator time:             " + str(self._FacilitatorTime)
        print "### Commentary time:              " + str(self._CommentaryTime)
        print "\n"


        self._ListOfTAsAndM2Ts.sort()
    
        tempcopy = []
        tempcopy = deepcopy(self._ListOfTAsAndM2Ts)
        
        for t in tempcopy:

            for f in self._DistrBeginnTimestamps:
                
                if self._DistrBeginnTimestamps[0] and t > self._DistrBeginnTimestamps[0]:
                    del self._DistrBeginnTimestamps[0]
                    del self._DistrEndTimestamps[0]
            

            distTemp = 0
            if (len(self._ListOfTAsAndM2Ts)>1) and self._ListOfTAsAndM2Ts[0] <= self._ListOfEOTs[0] and self._ListOfTAsAndM2Ts[1] <= self._ListOfEOTs[0]:
                

                if len(self._ListOfTAsAndM2Ts) > 1 and len(self._DistrBeginnTimestamps) > 0:
                    if self._DistrBeginnTimestamps[0] >= self._ListOfTAsAndM2Ts[0] and self._DistrBeginnTimestamps[0] <= self._ListOfTAsAndM2Ts[1]:
                        
                        
                        while(len(self._DistrBeginnTimestamps) > 0 and self._DistrBeginnTimestamps[0] >= self._ListOfTAsAndM2Ts[0] and self._DistrBeginnTimestamps[0] <= self._ListOfTAsAndM2Ts[1]):
                            distTemp = distTemp + (self._DistrEndTimestamps[0] - self._DistrBeginnTimestamps[0])
                            
                            del self._DistrEndTimestamps[0]
                            del self._DistrBeginnTimestamps[0]
                            
                        tagtime = self._ListOfTAsAndM2Ts[1] - self._ListOfTAsAndM2Ts[0]
                        tagtime = tagtime - distTemp
                            
                        
                    else:
                        tagtime = self._ListOfTAsAndM2Ts[1] - self._ListOfTAsAndM2Ts[0]
                        
                # thats the case, that there are no more distractions left
                elif len(self._ListOfTAsAndM2Ts) > 1:
                    tagtime = self._ListOfTAsAndM2Ts[1] - self._ListOfTAsAndM2Ts[0]
                
                # remove first element for next calculation
                del self._ListOfTAsAndM2Ts[0]
                self._TimesForTaggingPerItem.append(int(tagtime))
                #print tagtime
                

            else:
                del self._ListOfEOTs[0]
                del self._ListOfTAsAndM2Ts[0]
                
                
        #print self._TimesForTaggingPerItem
        


        # call csv writer and pass needed arguments
        csvwriter = testclass()
        csvwriter.run(self._overallTime, overallTimeWithoutDistr, self._stateTagging, teggingWithoutDistr, FMGTOverall,
                      FMGTWithoutDistr, self._sumOfDistractions, self._TaggingDistractions, FMGTDistractions, self._CommentaryTime,
                      self._TPInspectionTime, self._FacilitatorTime, self._numOfTags, float(avgTagsPerItem), self._numOfTp, self._numOfTd,
                      self._numOfTc,self._nrOfAssignedTags, self._filename, self._TimesForTaggingPerItem, self._numOfM2Ts)
        
        #logging.debug("p_expression_task_tagstore_storage recognized with start " + str(p[1]) + " and end " + str(p[3]))
        pass

    def p_expression_filemgt(self, p):
       ## file management state
       '''
       filemgt : TIMESTAMP MOVEFILETOTAGSTOREDRIVE NUMBER tagging filemgt
               | TIMESTAMP ENDTAGGINGTASK
               | distractions filemgt
               | commentdistractions filemgt
       ''' 
       logging.debug("p_expression_filemgt recognized")
       
       
       # End of State FileMGMT
       if p[2] == "eott":
        self._overallTime = int(p[1])
       
        
       if p[2] == "m2t":
        # calculate state tagging:
        # subtract beginning times from end times
        self._stateTagging -= int(p[1])
        
        # want to know the time a user spends while tagging one item, so need that timestamp
        self._ListOfTAsAndM2Ts.append(int(p[1]))
        
        # append begin timestamps of tagging state to a list
        self._TaggingBeginnTimestamps.append(int(p[1]))
        
        # count the number of moved items
        self._numOfItems += int(p[3])
        
        # count number of m2ts:
        self._numOfM2Ts += 1
        #print "m2t " + p[1]
        
        
    def p_expression_distractions(self, p):
       ## distractions meta state
       '''
       distractions : TIMESTAMP BEGININSPECTION TIMESTAMP ENDINSPECTION
                    | TIMESTAMP BEGINFACILITATOR WORD TIMESTAMP ENDFACILITATOR
                    | TIMESTAMP BEGINFACILITATOR WORDS TIMESTAMP ENDFACILITATOR				
       '''
       logging.debug("p_expression_commentdistr recognized")
       #print "1 im in distractions, and got "  + str(p[2])
       
       # need to treat "ib" distractions different than all others
       if p[2] == "ib":
        if p[3] and p[1]:
        # add timestamps of distractions to specific lists
            self._DistrBeginnTimestamps.append(int(p[1]))
            self._DistrEndTimestamps.append(int(p[3]))
        
            self._list1.append(int(p[1]))
            self._list2.append(int(p[3]))
        
       else:
        if p[4] and p[1]:
        # calculate facilitator time  
        # add timestamps of distractions to specific lists
            self._DistrBeginnTimestamps.append(int(p[1]))
            self._DistrEndTimestamps.append(int(p[4]))
        
            self._list3.append(int(p[1]))
            self._list4.append(int(p[4]))   
       
       logging.debug("p_expression_distractions recognized: " + p[1])

     
    def p_expression_commentdistractions(self, p):
       ## commentdistractions meta state
       '''
       commentdistractions : TIMESTAMP BEGINCOMMENTFACILITATOR WORDS multiplecomments
                           | TIMESTAMP BEGINCOMMENTFACILITATOR WORD multiplecomments
                           | TIMESTAMP BEGINCOMMENTFACILITATOR WORD TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINCOMMENTFACILITATOR WORDS TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINCOMMENTLOGGER WORDS multiplecomments
                           | TIMESTAMP BEGINCOMMENTLOGGER WORD multiplecomments
                           | TIMESTAMP BEGINCOMMENTLOGGER WORD TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINCOMMENTLOGGER WORDS TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINCOMMENTTP WORDS multiplecomments
                           | TIMESTAMP BEGINCOMMENTTP WORD multiplecomments
                           | TIMESTAMP BEGINCOMMENTTP WORD TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINCOMMENTTP WORDS TIMESTAMP ENDCOMMENT
                           | TIMESTAMP BEGINFACILITATOR WORDS multiplecomments
                           | TIMESTAMP BEGINFACILITATOR WORD multiplecomments
                           | TIMESTAMP BEGINFACILITATOR WORD TIMESTAMP ENDFACILITATOR
                           | TIMESTAMP BEGINFACILITATOR WORDS TIMESTAMP ENDFACILITATOR                         
       '''
        
       #logging.debug("p_expression_commentdistr2 recognized")
       if p[1]:
        self._DistrBeginnTimestamps.append(int(p[1]))
        self._list5.append(int(p[1]))
       if p[4]:
        self._DistrEndTimestamps.append(int(p[4]))
        self._list6.append(int(p[4]))
       

       
    def p_expression_multiplecomments(self, p):
       ## multiplecomments meta state
       '''
       multiplecomments :      TIMESTAMP BEGINCOMMENTFACILITATOR WORD TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTFACILITATOR WORDS TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTFACILITATOR WORDS multiplecomments
                             | TIMESTAMP BEGINCOMMENTFACILITATOR WORD multiplecomments
                             | TIMESTAMP BEGINCOMMENTLOGGER WORD TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTLOGGER WORDS TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTLOGGER WORDS multiplecomments
                             | TIMESTAMP BEGINCOMMENTLOGGER WORD multiplecomments
                             | TIMESTAMP BEGINCOMMENTTP WORD TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTTP WORDS TIMESTAMP ENDCOMMENT
                             | TIMESTAMP BEGINCOMMENTTP WORDS multiplecomments
                             | TIMESTAMP BEGINCOMMENTTP WORD multiplecomments
                             | TIMESTAMP BEGINFACILITATOR WORD TIMESTAMP ENDFACILITATOR
                             | TIMESTAMP BEGINFACILITATOR WORDS TIMESTAMP ENDFACILITATOR
                             | TIMESTAMP BEGINFACILITATOR WORDS multiplecomments
                             | TIMESTAMP BEGINFACILITATOR WORD multiplecomments
       '''

       if p[4]:
        self._DistrEndTimestamps.append(int(p[4]))
       #logging.debug("p_expression_commentdistr3 recognized")
        self._list6.append(int(p[4]))


    def p_expression_tagging(self, p):
        ## tagging state
       '''
       tagging : distractions tagging
               | commentdistractions tagging
               | TIMESTAMP ASSIGNTAGS NUMBER tagging
               | TIMESTAMP TAGPROPOSED tagging
               | TIMESTAMP TAGDEFAULT tagging
               | TIMESTAMP TAGCOMPLETION tagging
               | TIMESTAMP ENDOFTAGGING
       ''' 
       logging.debug("p_expression_tagging recognized" + str(p[1]))
            
       if p[2] == "eot":
        # add timestamps of state tagging to specific list
        self._TaggingEndTimestamps.append(int(p[1]))
        
        self._ListOfEOTs.append(int(p[1]))

        # check if this is the first tagging timestamp
        if self._stateTagging == 0:
            self._stateTagging = int(p[1])
        else:
            # add beginning times
            self._stateTagging += int(p[1])
     
       # count number of "tp" and number of tags    
       if p[2] == "tp":
        self._numOfTp += 1
        #self._numOfTags += 1

       # count number of "tc" and number of tags
       if p[2] == "tc":
        self._numOfTc += 1
        #self._numOfTags += 1
        
       # count number of "td" and number of tags
       if p[2] == "td":
        self._numOfTd += 1
        #self._numOfTags += 1
    
       # count how many tags were assigned
       if p[2] == "ta":
        self._numOfTags += int(p[3])
        self._nrOfAssignedTags.append(int(p[3]))
        
        # want to know the time a user spends while tagging one item, so need that timestamp
        self._ListOfTAsAndM2Ts.append(int(p[1]))
        
        #print "ta " + p[1] 

    def p_error(self, p):
        self._numerrors += 1
        if p:
            logging.critical("Syntax error at command '%s'" % p.value + " at linenumber: " + \
                              str(self._linenumber) + \
                              "\n  -> check if command exists" + \
                              "\n  -> check if closing command exists" + \
                              "\n  -> check if timestamp has proper format" + \
                              "\n  -> check if parameters are set correctly" + \
                              "\n  -> check if previous command is OK")
        else:
            logging.critical("Syntax error at EOF")
            


    def parse(self):
        self.expandedstring = self.__parser.parse(lexer=self.__lexer)

    

## end of parser filing_tagstore --------------------------

class testclass():

    def run(self, overallTime, overallTimeWithoutDistr, stateTagging, teggingWithoutDistr, FMGTOverall,
            FMGTWithoutDistr, sumOfDistractions, TaggingDistractions, FMGTDistractions, CommentaryTime,
            TPInspectionTime, FacilitatorTime, numOfTags, avgTagsPerItem, numOfTp, numOfTd, numOfTc,
            nrOfAssignedTags, filename, TimesForTaggingPerItem, numOfM2Ts):

        avgTagsPerItemKomma = str(round(avgTagsPerItem,2)).replace('.',',')

        
        list1= ["Overall time","Overall time without distr.", "Tagging time","Tagging time without distr.",
                "FMGT time","FMGT time without distr.", "Sum of distr.", "Tagging distr.", "FMGT distr.",
                "Commentary time", "TP Inspection time", "Facillitator time", "Sum of tags", "Avg Tags/Item",
                "#TP", "#TD", "#TC", "List #tags/item", "List of time user spent for tagging/item", "#m2t"]
        
        list2= [overallTime, overallTimeWithoutDistr, stateTagging, teggingWithoutDistr, FMGTOverall,
                FMGTWithoutDistr, sumOfDistractions, TaggingDistractions, FMGTDistractions, CommentaryTime,
                TPInspectionTime, FacilitatorTime, numOfTags, avgTagsPerItemKomma, numOfTp, numOfTd, numOfTc,
                str(nrOfAssignedTags)[1:-1], str(TimesForTaggingPerItem)[1:-1], numOfM2Ts]
        
        t_resultfile = filename[:-4] + "_results.csv"
        
        try:
            out = csv.writer(open(t_resultfile,"w"))
        except IOError, e:
            if e.errno==13:
                print "ERROR: Can't create csv file!"
                print "Please check if file is already opened and close it!\n"
                return
            else:
                print "ERROR: Can't create csv file!"
                return

        out = csv.writer(open(t_resultfile,"wb"), delimiter=';',quoting=csv.QUOTE_NONE)
        out.writerow(list1)

        out = csv.writer(open(t_resultfile,"a"), delimiter=';',quoting=csv.QUOTE_NONE)
        out.writerow(list2)
                
        print "CSV file " + t_resultfile + " successfully written in directory! \n"
        


def main():
    """Main function"""

    print "         UserLogAnalyzer.py - analyzes tshci userlog files\n"
    print "          (c) 2011 by Karl Voit <Karl.Voit@IST.TUGraz.at>"
    print "                             and"
    print "             Matija Striga <m.vrdoljak@student.TUGraz.at>"
    print "                   GPL v2 or any later version\n"

    (options, args) = cmd_line_parser.parse_args()

    handle_logging()

#    ## for (future) command line argument for checking only - if necessary)
#    global CHECKONLY
#    if options.checkonly:
#        logging.debug("checkonly is: %s" % options.checkonly ) 
#        CHECKONLY =  options.checkonly

    logging.debug("found arguments: " + str(args))

    ## check all given files (and stop if errors found:
    for file in args:
        if not os.path.isfile(file):
            logging.critical("Error: file \"" + str(file) + "\" is no file.")
            os.sys.exit(2)
        logging.debug("file \"" + str(file) + "\" is a valid, found file.")

    ## all files are found; handle file(s):
    for file in args:

        ## FIXXME: here needs to be a switch to the different parsers
        ## this can be done using command line argument like
        ##   $prog --filing-tagstore $file_with_logs_of_task_tagstore_filing.txt
        ## or with detecting some kind of file name convention like
        ##   TPxxa_t.txt -> "*a_t.txt" -> filing_tagstore
        
        logging.debug("initializing parser ...")
        ##lexer, tokens = filing_tagstore_lexer(file)
        parser = FilingTagstoreParser(file)
        logging.debug("running parser ...")
        parser.run()
        
        ## not working yet!
        #logging.debug("calling parser with lexer...")
        #parser = Filing_Tagstore_Parser(lexer, tokens)

 
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################
# vim:foldmethod=indent expandtab ai ft=python tw=120 fileencoding=utf-8 shiftwidth=4
