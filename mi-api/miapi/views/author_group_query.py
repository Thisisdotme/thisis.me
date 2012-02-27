'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession


log = logging.getLogger(__name__)


#
# AUTHOR GROUP QUERY: query for the highlights/details for a particular group (i.e. following)
#

class AuthorGroupQuery(object):
  '''
  classdocs
  '''
  
  '''
  class variables
  '''
  
  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request
      self.dbSession = DBSession()


  # GET /v1/authors/{authorname}/groups/{groupname}/highlights
  #
  # get the highlights for the author's group
  #
  def getHighlights(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
  
    return {'error':'not implemented'}

  # /v1/authors/{authorname}/groups/{groupname}/events
  #
  # get all events for the author's group
  #
  def getEvents(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
  
    return {'error':'not implemented'}

