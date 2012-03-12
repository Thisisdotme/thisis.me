'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy import (and_)

from miapi.models import DBSession

from mi_schema.models import Author, AuthorGroup, AuthorGroupMap, FeatureEvent, Feature, AuthorFeatureMap

from miapi.globals import LIMIT

from author_utils import createFeatureEvent

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
  ## THIS NEEDS TO MOVE BACK TO AuthorGroupQuery.getHighlights WHEN IMPLEMENTED
  @view_config(route_name='author.groups.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  #
  @view_config(route_name='author.groups.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def getEvents(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
  
    # get author-id for authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown author %s' % authorName}  
  
    # get feature-id for featureName
    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id == author.id,AuthorGroup.group_name == groupName)).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown feature %s' % authorName}  
  
    events = []  
    for fe,author,featureName in self.dbSession.query(FeatureEvent,Author,Feature.feature_name).join(AuthorFeatureMap,FeatureEvent.author_feature_map_id==AuthorFeatureMap.id).join(AuthorGroupMap,AuthorFeatureMap.author_id==AuthorGroupMap.author_id).join(Author,AuthorFeatureMap.author_id==Author.id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(AuthorGroupMap.author_group_id==authorGroup.id).filter(FeatureEvent.parent_id==None).order_by(FeatureEvent.create_time.desc()).limit(LIMIT):
      events.append(createFeatureEvent(self.dbSession,self.request,fe,featureName,author))
  
    return {'events':events,'paging':{'prev':None,'next':None}}
    
