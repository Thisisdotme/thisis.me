#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
import sys, csv, json

def main(argv):

  eventType = argv[1]
  sys.stderr.write(eventType)

#  reader = csv.reader(open("raw_json.csv", "rb"))
  reader = csv.reader(sys.stdin)

  for row in reader:

    authorId = int(row[0])
    jsonStr = row[1]

    if jsonStr is None:
      sys.stderr.write('ROW ERROR: %s.  Skipping row.' % json.dumps({'author_id':authorId,'message':'no JSON associated with authorId'}))
      continue

    jsonObj = json.loads(jsonStr)

    if authorId != jsonObj['author_id']:
      sys.stderr.write('ROW ERROR: %s.  Skipping row' % json.dumps({'author_id':authorId, 'json_author_id':jsonObj['author_id'], 'message':'inconsistent author_ids'}))
      continue

    # only collect events of the specified type
    if jsonObj["type"] == eventType:
      print json.dumps({'0.author_id':authorId,'1.event_id':jsonObj['event_id'],'2.time':jsonObj['create_time']}) + '\t' + row[1]

if __name__ == '__main__':
  main(sys.argv)
