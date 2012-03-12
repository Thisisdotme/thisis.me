'''
Created on Feb 22, 2012

@author: howard
'''
import logging

from sqlalchemy import (and_)

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, Feature, AuthorFeatureMap, FeatureEvent

from miapi.globals import LIMIT

from author_utils import createFeatureEvent

log = logging.getLogger(__name__)

#
# AUTHOR FEATURE QUERY: query for the highlights/details of the specified feature and author
#

class AuthorFeatureQuery(object):
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

  # GET /v1/authors/{authorname}/features/{featurename}/highlights
  #
  # return highlights for the feature
  #
  def getHighlights(self):
    
    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
    
    return {'error':'not implemented'}
  
  
  # GET /v1/authors/{authorname}/features/{featurename}/events'
  #
  # get all the featureEvent's for the author and feature  
  #
  ## THIS NEEDS TO MOVE BACK TO getHighlights WHEN IMPLEMENTED
  @view_config(route_name='author.features.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  ##
  @view_config(route_name='author.features.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  @view_config(route_name='author.features.featureEvents', request_method='GET', renderer='jsonp', http_cache=0)
  def getEvents(self):
  
    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
    
    # get author-id for authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown author %s' % authorName}  
  
    # get feature-id for featureName
    try:
      featureId, = self.dbSession.query(Feature.id).filter(Feature.feature_name == featureName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown feature %s' % authorName}  
  
    events = []  
    for fe,featureName in self.dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap,AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(and_(AuthorFeatureMap.feature_id==featureId,AuthorFeatureMap.author_id==author.id)).filter(FeatureEvent.parent_id==None).order_by(FeatureEvent.create_time.desc()).limit(LIMIT):
      events.append(createFeatureEvent(self.dbSession,self.request,fe,featureName,author))
  
    return {'events':events,'paging':{'prev':None,'next':None}}
