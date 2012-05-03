'''
Created on May 2, 2012

@author: howard
'''
import sys

from mi_utils.app_base import AppBase


class AuthorUpdater(AppBase):

  def display_usage(self):
    return "Usage: " + self.name + ".py\nExample: " + self.name + ".py"

  def main(self):
    self.log.info("Beginning: " + self.name)
    print self.config['AWS']['aws_access_key']
    print self.config['MySQL']['sqlalchemy.url']
    self.log.info("Finished: " + self.name)

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(AuthorUpdater(0).main())
