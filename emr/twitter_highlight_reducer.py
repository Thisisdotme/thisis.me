#!/usr/bin/python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, json, datetime

# only interested in the most recent of unique author/twitter_id tuples

NOW = datetime.datetime.now()

def computeSignal(retweetCount,favorited,currMin,currSpread,timestamp):

  # process
  retweetCount = retweetCount - currMin
  retweetStrength = int(round(float(retweetCount) / float(currSpread) * 100)) if currSpread > 0 else 0
  
  daysSinceEvent = (NOW - datetime.datetime.fromtimestamp(timestamp)).days
  recencyStrength = int(round(float(30-daysSinceEvent) / float(30) * 100))

  # if the tweet was been favorited then it's an automatic 100
  if favorited:
    retweetStrength = 100;
  
  return retweetStrength * recencyStrength

  
def main(argv):

  currAuthorId = None
  currMin = None
  currSpread = None


#  reader = open("part-00000", "rb")
  reader = sys.stdin
  
  for line in reader:

    (keyJSON, valueJSON) = line.strip().split("\t")

    keyIn = json.loads(keyJSON)
    valueIn = json.loads(valueJSON)
    
    authorId = keyIn['0.author_id']
    timestamp = keyIn['1.time']

    if currAuthorId == authorId:
      # output current tweet
      signal = computeSignal(valueIn['retweet_count'],valueIn['favorited'],currMin,currSpread,timestamp)
      if signal > 0:
        print "%s\t%d" % (json.dumps({'author_id':authorId,'id':valueIn['id'],'twitter_id':valueIn['twitter_id'],'retweet_count':valueIn['retweet_count'],'favorited':valueIn['favorited']}), signal)

    else:
      # transition to next authorId -- first row is always min/max
      currAuthorId = authorId
      currMin = valueIn['min_retweet_count']
      currSpread = valueIn['max_retweet_count'] - valueIn['min_retweet_count']
      

  if currAuthorId: 
    signal = computeSignal(valueIn['retweet_count'],valueIn['favorited'],currMin,currSpread,timestamp)
    if signal > 0:
      print "%s\t%d" % (json.dumps({'author_id':authorId,'id':valueIn['id'],'twitter_id':valueIn['twitter_id'],'retweet_count':valueIn['retweet_count'],'favorited':valueIn['favorited']}), signal)



if __name__ == '__main__':
  main(sys.argv)
