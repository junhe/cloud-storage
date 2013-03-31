#!/usr/bin/env python

import itertools,subprocess
import sys
from time import gmtime, strftime

filecounts = [100, 100, 100, 100,  10,    1]
filesizes =  [1,   10,  100, 1024, 10240, 102400] # KB

rndline = "asdjkl4321\n" # reason to use a psudo random string is that 
                         # generating too many random numbers is time
                         # consuming.
sn = 0
testdir = "testfiles/"
for i in range(0, 6):
    cnt = filecounts[i]
    sz = filesizes[i]
    print cnt, sz,

    nline = sz*1024/11
    for j in range(0, cnt):
        #fname = str(sz).zfill(4)+"."+str(j).zfill(4)+".txt"
        fname = testdir+str(sn)+".txt"
        sn = sn + 1
        print "Writing", fname, "..."
        f = open(fname, "w")
        for k in range(0, nline):
            f.write(rndline)


