#!/usr/bin/env python

import requests
from datetime import datetime
# Change this if you want to use it in 
# different places, for example jhecs553pa3.appspot.com or 
# localhost:8080
appurl = "http://localhost:8080"

def insert(fkey, fpath):
    """
    fkey is the key.
    fpath is the file path you want to upload
    return is the time of this operation
    """
    start_time = datetime.now()
    uploadurl = requests.get(appurl+"/uploadurl").text
    payload = {'filekey':fkey}
    files = {'file': open(fpath, 'r')}
    r = requests.post(uploadurl, data=payload, files=files)
    #print r.text
    end_time = datetime.now()
    return (end_time-start_time).total_seconds()

def check(fkey):
    start_time = datetime.now()
    payload = {'filekey':fkey}
    r = requests.post(appurl+"/check", data=payload)
    end_time = datetime.now()
    print r.text
    return (end_time-start_time).total_seconds()

def find(fkey):
    start_time = datetime.now()
    payload = {'filekey':fkey}
    r = requests.post(appurl+"/download", data=payload)
    end_time = datetime.now()
    print r.text
    return (end_time-start_time).total_seconds()

def remove(fkey):
    start_time = datetime.now()
    payload = {'filekey':fkey}
    r = requests.post(appurl+"/remove", data=payload)
    end_time = datetime.now()
    print r.text
    return (end_time-start_time).total_seconds()

def glist():
    start_time = datetime.now()
    r = requests.get(appurl+"/list")
    end_time = datetime.now()
    print r.text
    return (end_time-start_time).total_seconds()

def filesizelist():
    filecounts = [100, 100, 100, 100,  10,    1]
    filesizes =  [1,   10,  100, 1024, 10240, 102400] # KB
    sizestore = []
    sn = 0
    for i in range(0, 6):
        cnt = filecounts[i]
        sz = filesizes[i]
        for j in range(0, cnt):
            sizestore.append(sz)
            sn = sn + 1
    return sizestore



if __name__ == '__main__':
    print insert('1.txt', 'testfiles/1.txt')
    print check('1.txt')
    print find('1.txt')
    print remove('1.txt')
    print glist()
    
    filesizes = filesizelist()
    print filesizes
