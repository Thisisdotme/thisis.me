#!/usr/bin/python

'''
Created on Feb 27, 2012

@author: howard
'''
import sys, csv, json, datetime
import calendar

def main(argv):

  # get seconds for 30 days past
  start_date = datetime.date.today() + datetime.timedelta(-30)  
  start_secs = calendar.timegm(start_date.timetuple())

#  reader = csv.reader(open("part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:

    authorId = row[0]
    jsonStr = row[1]

    # make sure we have data
    if jsonStr is None:
      sys.stderr.write('ROW ERROR: %s.  Skipping row.' % json.dumps({'author_id':authorId,'message':'no JSON associated with authorId'}))
      continue

    jsonObj = json.loads(jsonStr)

    # make sure the data matches the author_id
    if authorId != str(jsonObj['author_id']):
      sys.stderr.write('ROW ERROR: %s.  Skipping row' % json.dumps({'author_id':authorId, 'json_author_id':jsonObj['author_id'], 'message':'inconsistent author_ids'}))
      continue

    # check if the event is in the last 30 days
    if jsonObj['create_time'] < start_secs:
      continue

    print row[0] + '\t' + row[1]

if __name__ == '__main__':
  main(sys.argv)
