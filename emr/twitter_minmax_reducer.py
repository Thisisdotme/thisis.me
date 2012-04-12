#!/usr/bin/python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, csv, json

  
def main(argv):

  currKey = None
  currMin = 0
  currMax = 0

#  reader = csv.reader(open("part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')
    
  for row in reader:

    authorId = int(row[0])
    valueJSON = row[1]

    valueObj = json.loads(valueJSON)

    if currKey == authorId:
      
      # update min/max and output row
          
      retweetCount = valueObj['_raw_json']['retweet_count']
      if retweetCount > currMax:
        currMax = retweetCount

      if retweetCount < currMin:
        currMin = retweetCount
      
      print "%s\t%s" % (json.dumps({'0.author_id':authorId,'1.time':valueObj['create_time']},sort_keys=True),valueJSON)

    else:

      if currKey:    
        # output current author's min/max
        print "%s\t%s" % (json.dumps({'0.author_id':currKey,'1.time':0},sort_keys=True),json.dumps({'min_retweet_count':currMin,'max_retweet_count':currMax}))

      # transition to new author
      currKey = authorId
      currMin = currMax = valueObj['retweet_count']
  
      print "%s\t%s" % (json.dumps({'0.author_id':authorId,'1.time':valueObj['create_time']},sort_keys=True),valueJSON)
        
  if currKey:
    # output current author's min/max
    print "%s\t%s" % (json.dumps({'0.author_id':currKey,'1.time':0},sort_keys=True),json.dumps({'min_retweet_count':currMin,'max_retweet_count':currMax}))


if __name__ == '__main__':
  main(sys.argv)
