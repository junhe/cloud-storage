#!/usr/bin/env python


import itertools,subprocess
import sys
from time import gmtime, strftime

nthreads = ["1","2","4","8"]
operations = ["insert", "find", "remove"]

parameters = [nthreads, operations]

paralist = list(itertools.product(*parameters))

jobid = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
logname = jobid + ".log"
resultname = jobid + ".result"


if __name__ == '__main__':
    logf = open(logname, 'a')
    resultf = open(resultname, 'a')
    header = "nthreads operation time"
    resultf.write(header + "\n")
    print header

    for rep in range(0,2):
        for para in paralist:
            print para,
            mycmd = "python runtest.py".split() + list(para)
            proc = subprocess.Popen(mycmd,
                           stdout=subprocess.PIPE,
                           stderr=logf)
            proc.wait()
            for line in proc.stdout:
                resultf.write( line + "\n" ) 
                sys.stdout.flush()
    
    logf.close()
    resultf.close()
