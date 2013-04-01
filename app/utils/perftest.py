#!/usr/bin/env python


import itertools,subprocess
import sys
from time import gmtime, strftime, sleep

nthreads = ["1","4"]
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
            print para
            sys.stdout.flush()
            mycmd = "python runtest.py".split() + list(para)
            proc = subprocess.Popen(mycmd,
                           stdout=subprocess.PIPE)
                           #stderr=logf)
            proc.wait()
            for line in proc.stdout:
                resultf.write( line ) 
                sys.stdout.flush()
            sleep(600) # slep for a while for consistency.
    
    logf.close()
    resultf.close()
