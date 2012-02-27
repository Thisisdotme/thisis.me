'''
Created on Jan 5, 2012

@author: howard
'''
import logging
import json

from datetime import datetime

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Author
from mi_schema.models import Feature
from mi_schema.models import AuthorFeatureMap

from miapi.models import DBSession

from author_utils import featureBuild

log = logging.getLogger(__name__)


##
##  author/feature relationship
##

# GET /v1/authors/{authorname}/features
#
# list all features associated with the author
@view_config(route_name='author.features', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatures(request):

  authorName = request.matchdict['authorname']

  dbsession = DBSession()

  try:
    authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown author %s' % authorName}

  features = []
  for feature in dbsession.query(Feature).join(AuthorFeatureMap).filter(Feature.id==AuthorFeatureMap.feature_id).join(Author).filter(AuthorFeatureMap.author_id==authorId).order_by(Feature.feature_name):
    features.append({'feature_id':feature.id,
                     'name':feature.feature_name,
                     'color_icon_high_res':request.static_url('miapi:%s' % feature.color_icon_high_res),
                     'color_icon_medium_res':request.static_url('miapi:%s' % feature.color_icon_medium_res),
                     'color_icon_low_res':request.static_url('miapi:%s' % feature.color_icon_low_res),
                     'mono_icon_high_res':request.static_url('miapi:%s' % feature.mono_icon_high_res),
                     'mono_icon_medium_res':request.static_url('miapi:%s' % feature.mono_icon_medium_res),
                     'mono_icon_low_res':request.static_url('miapi:%s' % feature.mono_icon_low_res)})

  return {'author_name':authorName,'features':features}


# GET /v1/authors/{authorname}/features/{featurename}
# 
# get info & configuration details for the author's feature
#
@view_config(route_name='author.features.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatureInfo(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']

  dbsession = DBSession()

  try:
    authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown author %s' % authorName}

  try:
    featureId, = dbsession.query(Feature.id).filter_by(feature_name=featureName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown feature %s' % featureName}

  try:
    afm = dbsession.query(AuthorFeatureMap).filter_by(author_id=authorId,feature_id=featureId).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown feature for author'}
  
  response = {'author':authorName,'feature':featureName,'last_update_time': datetime.isoformat(afm.last_update_time) if afm.last_update_time else None}

  if afm.access_token:
    response['access_token'] = afm.access_token

  if afm.access_token_secret:
    response['access_token_secret'] = afm.access_token_secret

  if afm.auxillary_data:
    response['auxillary_data'] = json.loads(afm.auxillary_data)

  return response


# PUT /v1/authors/{authorname}/features/{featurename}
#
# add the feature to the author's feature set
#
@view_config(route_name='author.features.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def authorFeatureAdd(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']

  credentials = request.json_body
  accessToken = credentials.get('access_token')
  accessTokenSecret = credentials.get('access_token_secret')

  # check for auxillary data and convert to a string if it exists
  auxillaryData = credentials.get('auxillary_data')
  if auxillaryData:
    auxillaryData = json.dumps(auxillaryData)
  
  dbsession = DBSession()

  try:
    authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown author %s' % authorName}

  try:
    featureId, = dbsession.query(Feature.id).filter_by(feature_name=featureName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown feature %s' % featureName}

  authorFeatureMap = AuthorFeatureMap(authorId,featureId,accessToken,accessTokenSecret,auxillaryData)

  try:
    dbsession.add(authorFeatureMap)
    dbsession.commit()
    log.info("created author/feature link: %s -> %s" % (authorName,featureName))

  except IntegrityError, e:
    dbsession.rollback()
    request.response.status_int = 409
    return {'error':e.message}

  # load events for this feature
  s3Bucket = request.registry.settings.get('mi.s3_bucket')
  awsAccessKey = request.registry.settings.get('mi.aws_access_key')
  awsSecretKey = request.registry.settings.get('mi.aws_secret_key')
  featureBuild(authorName,featureName,False,s3Bucket,awsAccessKey,awsSecretKey)

  response = {'author':authorName,'feature':featureName}

  if accessToken:
    response['access_token'] = accessToken

  if accessTokenSecret:
    response['access_token_secret'] = accessTokenSecret
    
  if auxillaryData:
    response['auxillary_data'] = json.loads(auxillaryData)
  
  dbsession.close()

  return response


# delete the feature from the author's feature set
#
@view_config(route_name='author.features.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def authorFeatureRemove(request):

  authorname = request.matchdict['authorname']
  featurename = request.matchdict['featurename']

  dbsession = DBSession()

  author = dbsession.query(Author).filter_by(author_name=authorname).first()
  if author == None:
    request.response.status_int = 404
    return {'error':'unknown authorname'}

  feature = dbsession.query(Feature).filter_by(feature_name=featurename).first()
  if feature == None:
    request.response.status_int = 404
    return {'error':'unknown feature'}

  authorFeatureMap = dbsession.query(AuthorFeatureMap).filter_by(author_id=author.id,feature_id=feature.id).first()
  if not authorFeatureMap:
    request.response.status_int = 404
    return {'error':'unknown feature for author'}

  try:
    dbsession.delete(authorFeatureMap)
    dbsession.commit()
  
  except Exception:
    dbsession.rollback();
    raise

  return {}

