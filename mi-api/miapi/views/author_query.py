'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import (Author, Feature, FeatureEvent, AuthorFeatureMap)

from author_utils import createFeatureEvent

log = logging.getLogger(__name__)

LIMIT = 200

##
## author FeatureEvents functionality
##

class AuthorQuery(object):
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


  # GET /v1/authors/{authorname}/highlights
  #
  # get the event highlights for the author
  #
  def getHighlights(self):

    authorName = self.request.matchdict['authorname']
  
    return {'error':'not implemented'}

  
  # GET /v1/authors/{authorname}/events
  #
  # get all FeatureEvents for the author (constrained to query arg. filters)
  #
  ## THIS NEEDS TO MOVE BACK TO self.getHighlights WHEN IMPLEMENTED
  @view_config(route_name='author.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  ##
  ##  
  @view_config(route_name='author.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  @view_config(route_name='author.featureEvents', request_method='GET', renderer='jsonp', http_cache=0) # deprecated
  def getEvents(self):
  
    authorName = self.request.matchdict['authorname']
    
    # get author-id for authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown author %s' % authorName}  
    
    events = []  
    for fe,featureName in self.dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap, AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(AuthorFeatureMap.author_id==author.id).filter(FeatureEvent.parent_id==None).order_by(FeatureEvent.create_time.desc()).limit(LIMIT):
      events.append(createFeatureEvent(self.dbSession,self.request,fe,featureName,author))
  
    return {'events':events,'paging':{'prev':None,'next':None}}


  # GET /v1/authors/{authorname}/events/{eventID}
  #
  # get details for the featureEvent
  #
  @view_config(route_name='author.query.events.eventId', request_method='GET', renderer='jsonp', http_cache=0)
  @view_config(route_name='author.featureEvents.featureEvent', request_method='GET', renderer='jsonp', http_cache=0) # deprecated
  def getEventDetail(self):
    
    authorName = self.request.matchdict['authorname']
    featureEventID = int(self.request.matchdict['eventID'])
  
    dbSession = DBSession()
  
    # get author-id for authorName
    try:
      author = dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown author %s' % authorName}  
  
    fe,featureName = dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap, AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(FeatureEvent.id==featureEventID).filter(AuthorFeatureMap.author_id==author.id).one()
  
    return {'event':createFeatureEvent(dbSession,self.request,fe,featureName,author)}
