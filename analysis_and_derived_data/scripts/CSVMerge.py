import csv
import os
import glob

path = './'
c = 0
#path = dir(raw_input("Enter the path: "))


print "\n  CSVMerge.py - Merges TPXX CSV result files into one file"
print "        Matija Striga <m.vrdoljak@student.TUGraz.at>"

print "\n\nPlease note, that the CSV Files you want to merge must all be in the same folder as this script!"
print "Please use different folders for different tasks (Tagging, Filing, Refinding).\n"

try:
    out = csv.writer(open("all_results.csv","w"))
    
except IOError, e:
    if e.errno==13:
        print "ERROR: Can't create csv file!"
        print "Please check if file is already opened and close it!\n"
    else:
        print "ERROR: Can't create csv file!"

for infile in glob.glob( os.path.join(path, 'TP*.csv') ):
    print "Merging... " + infile
    spamReader = csv.reader(open(infile, "r"))
    if c > 0:
        spamReader.next()
        for row in spamReader:
            #print row
        
            out.writerow(row)
    else:
        for row in spamReader:
            out.writerow(row)
    c += 1
    
print "\nFinished!"