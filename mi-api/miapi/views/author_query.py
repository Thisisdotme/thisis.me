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


##
## author FeatureEvents functionality
##


#/v1/authors/{authorname}/highlights
# get the event highlights for the author
@view_config(route_name='author.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
def authorHighlights(request):

  dbSession = DBSession()

  authorName = request.matchdict['authorname']

  return {'error':'not implemented'}


# /v1/authors/{authorname}/events
# get all FeatureEvents for the author (constrained to query arg. filters)
#
@view_config(route_name='author.query.events', request_method='GET', renderer='jsonp', http_cache=0)
@view_config(route_name='author.featureEvents', request_method='GET', renderer='jsonp', http_cache=0) # deprecated
def authorEvents(request):
  
  authorName = request.matchdict['authorname']
  
  dbSession = DBSession()

  # get author-id for authorName
  try:
    authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()
  except:
    request.response.status_int = 404;
    return {'error':'unknown author %s' % authorName}  
  
  events = []  
  for fe,featureName in dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap, AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(AuthorFeatureMap.author_id==authorId).order_by(FeatureEvent.create_time.desc()).all():
    events.append(createFeatureEvent(request,fe,featureName))

  return {'events':events,'paging':{'prev':None,'next':None}}


# /v1/authors/{authorname}/events/{eventID}
# get details for the featureEvent
@view_config(route_name='author.query.events.eventId', request_method='GET', renderer='jsonp', http_cache=0)
@view_config(route_name='author.featureEvents.featureEvent', request_method='GET', renderer='jsonp', http_cache=0) # deprecated
def authorEventInfo(request):

  authorName = request.matchdict['authorname']
  featureEventID = int(request.matchdict['eventID'])

  dbSession = DBSession()

  # get author-id for authorName
  try:
    authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()
  except:
    request.response.status_int = 404;
    return {'error':'unknown author %s' % authorName}  

  fe,featureName = dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap, AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(FeatureEvent.id==featureEventID).filter(AuthorFeatureMap.author_id==authorId).one()

  return {'event':createFeatureEvent(request,fe,featureName)}

