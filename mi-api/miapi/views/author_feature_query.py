'''
Created on Feb 22, 2012

@author: howard
'''
import logging

from sqlalchemy import (and_)

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, Feature, AuthorFeatureMap, FeatureEvent

from author_utils import createFeatureEvent

log = logging.getLogger(__name__)


#
# AUTHOR FEATURE QUERY: query for the highlights/details of the specified feature and author
#

# return highlights for the feature
#

# GET /v1/authors/{authorname}/features/{featurename}/highlights
#
@view_config(route_name='author.features.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatureHighlights(request):
  
  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']
  
  return {'error':'not implemented'}


# GET /v1/authors/{authorname}/features/{featurename}/events'
#
# get all the featureEvent's for the author and feature

#
@view_config(route_name='author.features.query.events', request_method='GET', renderer='jsonp', http_cache=0)
@view_config(route_name='author.features.featureEvents', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatureEvents(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']
  
  dbSession = DBSession()

  # get author-id for authorName
  try:
    authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()
  except:
    request.response.status_int = 404;
    return {'error':'unknown author %s' % authorName}  

  # get feature-id for featureName
  try:
    featureId, = dbSession.query(Feature.id).filter(Feature.feature_name == featureName).one()
  except:
    request.response.status_int = 404;
    return {'error':'unknown feature %s' % authorName}  

  events = []  
  for fe,featureName in dbSession.query(FeatureEvent,Feature.feature_name).join(AuthorFeatureMap,AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).join(Feature,AuthorFeatureMap.feature_id==Feature.id).filter(and_(AuthorFeatureMap.feature_id==featureId,AuthorFeatureMap.author_id==authorId)).order_by(FeatureEvent.create_time.desc()).all():
    events.append(createFeatureEvent(request,fe,featureName))

  return {'events':events,'paging':{'prev':None,'next':None}}


