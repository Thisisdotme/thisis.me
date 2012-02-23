'''
Created on Jan 16, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from mi_schema.models import Feature, Author, AuthorFeatureMap

from mi_profile_retrieval.profile_retriever_factory import ProfileRetrievalFactory

from miapi.models import DBSession

from miapi import oAuthConfig

log = logging.getLogger(__name__)


# get all the featureEvent's for the author and feature
@view_config(route_name='author.features.profile', request_method='GET', renderer='jsonp', http_cache=0)
def feature_profile(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']

  retriever = ProfileRetrievalFactory.get_retriever_for(featureName)
  if not retriever:
    request.response.status_int = 404
    return {'error':'profile information is not available for feature %s' % featureName}  
    
  db_session = DBSession()

  # get author-id for authorName
  try:
    author_id, = db_session.query(Author.id).filter(Author.author_name == authorName).one()
  except:
    request.response.status_int = 404
    return {'error':'unknown author %s' % authorName}  

  # get feature-id for featureName
  try:
    feature_id, = db_session.query(Feature.id).filter(Feature.feature_name == featureName).one()
  except:
    request.response.status_int = 404
    return {'error':'unknown feature %s' % authorName}  

  try:
    mapping = db_session.query(AuthorFeatureMap).filter_by(feature_id=feature_id,author_id=author_id).one()
  except:
    request.response.status_int = 404
    return {'error':'unknown feature for author'}

  profileJSON = retriever.get_author_profile(mapping,db_session,oAuthConfig.get(featureName))

  db_session.close()

  return profileJSON
