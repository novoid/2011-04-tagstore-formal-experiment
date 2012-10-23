#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from fnmatch import fnmatch
import string
import os.path
import glob
import collections
import re
import fnmatch

from os.path import join, isdir, islink
from os import error, listdir
excludes = ['*.py', '*.DS_Store']
excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
start = '.'
#root = '.'
# for root, dirs, files in walk2('.'):
#         files = [os.path.join(root, f) for f in files]
#         files = [f for f in files if not re.match(excludes, f)]    
levelstart = start.count(os.sep)
level = start.count(os.sep) - levelstart
for start, dirs, files in os.walk(start):
  files = [os.path.join(start, f) for f in files]
  files = [f for f in files if not re.match(excludes, f)]  
  level = start.count(os.sep) - levelstart
def walk2(top, topdown=True, onerror=None, deeplevel=0):
    try:
        names = listdir(top)
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if isdir(join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs, deeplevel
    for name in dirs:
        path = join(top, name)
        if not islink(path):
            for x in walk2(path, topdown, onerror, deeplevel+1):
                yield x
    if not topdown:
        yield top, dirs, nondirs, deeplevel


if __name__ == '__main__':
  
    for top, dirs, files, deeplevel in walk2('.'):
        files = [os.path.join(start, f) for f in files]
        files = [f for f in files if not re.match(excludes, f)]
        print "[Level:]", deeplevel, ':', "[DIRS]", len(dirs), ' ' * 4, "[files_in_folder:]", len(files)
####    
for top, dirs, files in os.walk(top):
    dir1 = len(dirs)
    if dirs == []:
       continue
    print level, ':', dir1


print "allFolders", sum([len(dirs) for root, dirs, files in os.walk('.')])


################################################################################
#print len(os.walk('.').next()[0])
# print "len(os.walk('.').next()", len(os.walk('.').next()[1])
# ##print len(os.walk('.').next()[2])
# #print len(os.walk('.').next()[3])
top = '.'
startinglevel = top.count(os.sep)
for top, dirs, files in os.walk(top):
   level = top.count(os.sep) - startinglevel
#   #level1 = level.count(os.sep)
   dir1 = len(dirs)

   if dirs == []:
      continue
   print level, ':', dir1

  #print len(os.walk('.').next())
  ##print level, "---", len([level for level in os.listdir(top) if os.path.isdir(os.path.join(top, level))])
  #print dirs in level if os.path.join(somedir, level)
  #print len(dirs), "sdf", level
  #print len(os.walk(top).next())

for (path, dirs, files) in os.walk('.'):

    dirs = join(dirs)
    dirs = str(dirs)
    lst = list(dirs)
    
    if dirs == "[]":
        break
    else:   
        #print len(dirs), dirs
        print "lst", len(lst)

    

print "####################################"   
for dirname, dirnames, filenames in os.walk('.'):
    for subdirname in dirnames:
        print len(dirname), dirname, len(subdirname), subdirname
print "####################################"   
      

        
print "####################################"  
lon = [] 
for dirname, dirnames, filenames in os.walk('.'):
    for subdirname in dirnames:
        
        #print len(subdirname)
        lon = sum([len(subdirname)])
        #lon = len(subdirname)
        #lon2 = list(lon)
        #print lon
        print lon




fileList = []
fileSize = 0
folderCount = 0
for root, subFolders, files in os.walk('.'):
    folderCount += len(subFolders)
    for file in files:
        f = os.path.join(root,file)
        fileSize = fileSize + os.path.getsize(f)
        #print(f)
        fileList.append(f)

print("Total Size is {0} bytes".format(fileSize))
print("Total Files ", len(fileList))
print("Total Folders ", folderCount)
path = '.'
for (path, dirs, files) in os.walk(path):

    dirs = " ".join(dirs)
    #dirs = str(dirs)
    dirs = sum([len(str(dirs))])
    mylist = str(dirs)
    #if dirs == "[]":
      #  None
  #  else:   
        #print list(dirs), len(dirs)
        #print dirs
        #print str(mylist)
    #print ''.join(map(str, mylist))
    #print [ x.rstrip() for x in mylist ]
    #print [mylist]
    print "sadf", dirs
    #print sum(mylist)
        #print reduce(lambda x, y: x+y, [dirs])
        
## sum([len(foldername) for foldername in dirs])
