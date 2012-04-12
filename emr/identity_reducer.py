#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
  
import sys, csv, json

def main(argv):

  (last_key, max_val) = (None, 0)
  for line in sys.stdin:

    (key, val) = line.strip().split("\t")

    if last_key and last_key != key:
#      print "%s\t%s" % (last_key, max_val)
#      (last_key, max_val) = (key, int(val))
      print "%s\t%s" % (key,val)
      
    else:
#      (last_key, max_val) = (key, max(max_val, int(val)))
      print "%s\t%s" % (key,val)
  
#  if last_key:
#    print "%s\t%s" % (last_key, max_val)


if __name__ == '__main__':
  main(sys.argv)
