#!/usr/bin/python

'''
Created on Feb 27, 2012

@author: howard
'''
import sys, csv, json

def main(argv):
  
#  reader = csv.reader(open("part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    keyIn = json.loads(row[0])
    valueIn = json.loads(row[1])

    key = {}
    key['0.author_id'] = keyIn['0.author_id']
    key['1.time'] = keyIn['1.time']
    
    value = None
    # check if this is the row carrying our min/max and pass-through if so
    if int(key['1.time']) == 0:
      value = valueIn
    else:
      value = {}
      value['id'] = valueIn['id']
      value['twitter_id'] = valueIn['_raw_json']['id_str']
      value['retweet_count'] = valueIn['_raw_json'].get('retweet_count',0)
      value['favorited'] = valueIn['_raw_json'].get('favorited',False)
      
    print json.dumps(key,sort_keys=True) + '\t' + json.dumps(value,sort_keys=True)
    

if __name__ == '__main__':
  main(sys.argv)
