#!/usr/bin/env python

'''
Created on Apr 5, 2012

@author: howard
'''
  
import sys, csv, json

def main(argv):

  maxId = None
  maxTime = 0

  (currKey, count) = (None, 0)

#  reader = csv.reader(open("foursquare/map.out", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    keyIn = json.loads(row[0])

    cursorKey = (keyIn['1.author_id'],keyIn['2.venue_id']) 

    if currKey and currKey != cursorKey:

      # transition to next key

      # need to have check-in more than once
      if count > 1:
        keyOut = {}
        keyOut['1.author_id'] = currKey[0]
        keyOut['2.venue_id'] = currKey[1]
        keyOut['3.time'] = maxTime
        keyOut['4.id'] = maxId
  
        print "%s\t%d" % (json.dumps(keyOut,sort_keys=True), count)

      (currKey, count) = (cursorKey, 1)
      maxTime = keyIn['3.time']
      maxId = keyIn['4.id']

    else:
      
      # still processing the same key
      if keyIn['3.time'] > maxTime:
        maxTime = keyIn['3.time']
        maxId = keyIn['4.id']
  
      (currKey, count) = (cursorKey, count + 1)
  
  if currKey:
    if count > 1:
      keyOut = {}
      keyOut['1.author_id'] = currKey[0]
      keyOut['2.venue_id'] = currKey[1]
      keyOut['3.time'] = maxTime
      keyOut['4.id'] = maxId
    
      print "%s\t%d" % (json.dumps(keyOut,sort_keys=True), count)


if __name__ == '__main__':
  main(sys.argv)
