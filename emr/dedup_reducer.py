#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, csv, json

# only interested in the most recent of unique author/twitter_id tuples

def main(argv):

  (activeKey,activeValue) = (None, None)

#  reader = csv.reader(open("linkedin/map.out", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    keyIn = json.loads(row[0])

    currKey = (keyIn['0.author_id'], keyIn['1.event_id'])

    # skip duplicates
    if activeKey == currKey:
      sys.stderr.write("WARNING: DUPLICATE ROW - skipping")
      continue  

    else:

      # transition to new key
      if activeKey:
        print "%d\t%s" % (activeKey[0], activeValue)
      
      (activeKey,activeValue) = (currKey,row[1])
        

  if activeKey:
    print "%d\t%s" % (activeKey[0], activeValue)
    

if __name__ == '__main__':
  main(sys.argv)
