#!/usr/bin/env python

'''
Created on Feb 27, 2012

@author: howard
'''
import sys, csv

def main(argv):

#  reader = csv.reader(open("part-00000", "rb"),delimiter='\t')
  reader = csv.reader(sys.stdin,delimiter='\t')

  for row in reader:
    print row[0] + '\t' + row[1]

if __name__ == '__main__':
  main(sys.argv)
