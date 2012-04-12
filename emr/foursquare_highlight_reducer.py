#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, csv, json, datetime

# only interested in the most recent of unique author/twitter_id tuples

NOW = datetime.datetime.now()

def computeSignal(checkinCount,currMin,currSpread,timestamp):

  # process
  checkinCount = checkinCount - currMin
  retweetStrength = (int(round((float(checkinCount) / float(currSpread) if currSpread > 0 else 1) * 100)))
  
  daysSinceEvent = (NOW - datetime.datetime.fromtimestamp(timestamp)).days
  recencyStrength = int(round(float(30-daysSinceEvent) / float(30) * 100))
  
  return retweetStrength * recencyStrength

  
def main(argv):

  activeAuthorId = None
  currKey = None
  currValue = None
  currMin = None
  currSpread = None


#  reader = csv.reader(open("part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    currKey = json.loads(row[0])
    currValue = row[1]
    
    authorId = currKey['1.author_id']
    timestamp = currKey['3.time']

    if activeAuthorId == authorId:
      # output current checkin weight
      value = int(currValue)
      weight = computeSignal(value,currMin,currSpread,timestamp)
      if weight > 0:
        currKey['5.count'] = value
        print "%s\t%d" % (json.dumps(currKey,sort_keys=True), weight)

    else:
      # transition to next authorId -- first row is always min/max
      activeAuthorId = authorId
      valueIn = json.loads(currValue)
      currMin = valueIn['min_count']
      currSpread = valueIn['max_count'] - valueIn['min_count']
      

  if activeAuthorId: 
    value = int(currValue)
    weight = computeSignal(value,currMin,currSpread,timestamp)
    if weight > 0:
      currKey['5.count'] = value
      print "%s\t%d" % (json.dumps(currKey,sort_keys=True), weight)



if __name__ == '__main__':
  main(sys.argv)
