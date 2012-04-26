'''
Created on Apr 24, 2012

@author: howard
'''
import logging, json

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from mi_schema.models import Author, Feature, AuthorFeatureMap, AuthorFeatureDefault

from miapi.models import DBSession

from .feature_utils import getAuthorFeatures

log = logging.getLogger(__name__)

class AuthorFeatureController(object):
  '''
  classdocs
  '''

  def __init__(self, request):
    '''
    Constructor
    '''
    self.request = request
    self.dbSession = DBSession()

  # GET /v1/authors/{authorname}/features
  #
  # list all services associated with the author
  @view_config(route_name='author.features', request_method='GET', renderer='jsonp', http_cache=0)
  def listAuthorFeatures(self):
  
    authorName = self.request.matchdict['authorname']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    features = getAuthorFeatures(self.dbSession,authorId)
  
    return {'author_name':authorName,'features':features}
  

  # PUT /v1/authors/{authorname}/services/{featurename}
  #
  # add the feature to the author's feature set
  #
  @view_config(route_name='author.features.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def putAuthorFeature(self):
  
    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      featureId, = self.dbSession.query(Feature.id).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature %s' % featureName}

    # get the max feature sequence for this author
    maxSequence, = self.dbSession.query(func.max(AuthorFeatureMap.sequence)).filter(AuthorFeatureMap.author_id==authorId).one()
    if not maxSequence:
      maxSequence = 0
    
    authorFeatureMap = AuthorFeatureMap(authorId,featureId,maxSequence+1)
  
    try:
      self.dbSession.add(authorFeatureMap)
      self.dbSession.flush()
      self.dbSession.commit()
      log.info("created author/feature link: %s -> %s" % (authorName,featureName))
  
    except IntegrityError, e:
      self.dbSession.rollback()
      self.request.response.status_int = 409
      return {'error':e.message}
  
    response = {'author':authorName,'feature':featureName}
  
    self.dbSession.close()
  
    return response


  # delete the feature from the author's feature set
  #
  @view_config(route_name='author.features.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteAuthorService(self):
  
    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
  
    try:
      authorId,= self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      featureId, = self.dbSession.query(Feature.id).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature %s' % featureName}

    try:
      authorFeatureMap = self.dbSession.query(AuthorFeatureMap).filter_by(author_id=authorId,feature_id=featureId).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature for author'}
  
    try:
      self.dbSession.delete(authorFeatureMap)
      self.dbSession.commit()
    
    except Exception:
      self.dbSession.rollback();
      raise
  
    return {}


  # GET /v1/authors/{authorname}/features/{featurename}
  # 
  # get info & configuration details for the author's feature
  #
  @view_config(route_name='author.features.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getAuthorServiceInfo(self):
  
    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      serviceId, = self.dbSession.query(Feature.id).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature %s' % featureName}
  
    try:
      afm = self.dbSession.query(AuthorFeatureMap).filter_by(author_id=authorId,feature_id=serviceId).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature for author'}
    
    response = {'author':authorName,'feature':featureName, 'sequence':afm.sequence}
    
    return response


  # GET /v1/authors/{authorname}/features/default
  #
  @view_config(route_name='author.features.default', request_method='GET', renderer='jsonp', http_cache=0)
  def getDefaultFeature(self):

    authorName = self.request.matchdict['authorname']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    # it's OK for no default to exists.  The convention if no explicit default exists is to use the first feature
    try:
      featureName, = self.dbSession.query(Feature.name).join(AuthorFeatureDefault,Feature.id==AuthorFeatureDefault.feature_id).filter(AuthorFeatureDefault.author_id==authorId).one()
    except NoResultFound:
      featureName = None

    result = {'author':authorName,'default_feature':featureName}
    
    return result


  @view_config(route_name='author.features.default.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def setDefaultFeature(self):

    authorName = self.request.matchdict['authorname']
    featureName = self.request.matchdict['featurename']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      featureId, = self.dbSession.query(Feature.id).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown feature %s' % featureName}

    # if a default already exists then remove it
    try:
      afd = self.dbSession.query(AuthorFeatureDefault).filter_by(author_id=authorId).one()
      self.dbSession.delete(afd)
    except NoResultFound:
      pass
    
    afd = AuthorFeatureDefault(authorId,featureId)
    self.dbSession.add(afd)
    
    self.dbSession.commit()
    
    return {'author':authorName,'default_feature':featureName}
