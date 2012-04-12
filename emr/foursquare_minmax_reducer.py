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

    key = json.loads(row[0])
    value = int(row[1])

    if currKey and currKey['1.author_id'] == key['1.author_id']:
      
      # update min/max and output row
          
      if value > currMax:
        currMax = value

      if value < currMin:
        currMin = value
      
      print "%s\t%d" % (row[0],value)

    else:

      if currKey:    
        currKey['2.venue_id'] = "0"
        currKey['3.time'] = 0
        currKey['4.id'] = 0

        # output current author's min/max
        print "%s\t%s" % (json.dumps(currKey,sort_keys=True),json.dumps({'min_count':currMin,'max_count':currMax}))

      # transition to new author
      currKey = key
      currMin = currMax = value
  
      print "%s\t%d" % (row[0],value)
        
  if currKey:    
    currKey['2.venue_id'] = "0"
    currKey['3.time'] = 0
    currKey['4.id'] = 0
    # output current author's min/max
    print "%s\t%s" % (json.dumps(currKey,sort_keys=True),json.dumps({'min_count':currMin,'max_count':currMax}))
  

if __name__ == '__main__':
  main(sys.argv)
