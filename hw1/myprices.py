#!/usr/bin/python3
import sys
from yahoo_finance import Share
from pprint import pprint
import time

if len(sys.argv) != 2:  # the program name and the datafile
  # stop the program and print an error message
  sys.exit("usage: read1.py datafile ")

filename = sys.argv[1]

print("input", sys.argv[1])

try:
    with open(filename, 'r') as f:
        lines = f.readlines()
except (IOError, FileNotFoundError):
    print ("Cannot open file {}".format(filename))
    sys.exit("bye")

count = 1
prices = {}
start = time.clock()
for line in lines:
    thisline = line.split()
    if len(line) > 0:
        #print (str(count) + " " + thisline[0])
        share = Share(thisline[0])
        everything = share.get_historical('2015-01-01', '2015-01-15')
        prices[thisline[0]] = [0 for j in range(len(everything))]
        for j in range(len(everything)):
            #print(str(j) + " price: " + everything[j]['Adj_Close'])
            prices[thisline[0]][j] = float(everything[j]['Adj_Close'])

#        print prices[thisline[0]]
        count += 1
print(time.clock() - start)
print(prices['DDD'])
