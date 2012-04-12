#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, csv, json, datetime

NOW = datetime.datetime.now()

def computeSignal(connectCount,timestamp):

  # process
  connectStrength = int(round(float(connectCount) / float(30) * 100))
  
  daysSinceEvent = (NOW - datetime.datetime.fromtimestamp(timestamp)).days
  recencyStrength = int(round(float(30-daysSinceEvent) / float(30) * 100))
  
  return connectStrength * recencyStrength

 
def main(argv):

  activeKey = None
  maxId = None
  maxTime = 0
  count = 0

#  reader = csv.reader(open("linkedin/part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    currKey = json.loads(row[0])

    if activeKey and activeKey['0.author_id'] != currKey['0.author_id']:

      weight = computeSignal(count,maxTime)
      if weight > 0:

        activeKey['1.time'] = maxTime
        activeKey['2.id'] = maxId
        activeKey['3.count'] = count
  
        print "%s\t%d" % (json.dumps(activeKey,sort_keys=True), weight)

      # transition to next key
      activeKey = currKey
      count = 1
      maxTime = currKey['1.time']
      maxId = currKey['2.id']

    else:
      
      # still processing the same key
      if currKey['1.time'] > maxTime:
        maxTime = currKey['1.time']
        maxId = currKey['2.id']
  
      activeKey = currKey
      count = count + 1
  
  if activeKey:

    weight = computeSignal(count,maxTime)
    if weight > 0:
      activeKey['1.time'] = maxTime
      activeKey['2.id'] = maxId
      activeKey['3.count'] = count

      print "%s\t%d" % (json.dumps(activeKey,sort_keys=True), weight)


if __name__ == '__main__':
  main(sys.argv)
