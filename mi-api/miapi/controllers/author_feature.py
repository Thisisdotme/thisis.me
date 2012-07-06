'''
Created on Apr 24, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from tim_commons import db

from mi_schema.models import Author, Feature, AuthorFeatureMap, AuthorFeatureDefault

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
    self.db_session = db.Session()

  # GET /v1/authors/{authorname}/features
  #
  # list all services associated with the author
  @view_config(route_name='author.features', request_method='GET', renderer='jsonp', http_cache=0)
  def listAuthorFeatures(self):

    author_name = self.request.matchdict['authorname']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    features = getAuthorFeatures(self.db_session, author_id)

    return {'author_name': author_name, 'features': features}

  # PUT /v1/authors/{authorname}/services/{featurename}
  #
  # add the feature to the author's feature set
  #
  @view_config(route_name='author.features.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def putAuthorFeature(self):

    author_name = self.request.matchdict['authorname']
    feature_name = self.request.matchdict['featurename']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      feature_id, = self.db_session.query(Feature.id).filter_by(name=feature_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature %s' % feature_name}

    # get the max feature sequence for this author
    maxSequence, = self.db_session.query(func.max(AuthorFeatureMap.sequence)).filter(AuthorFeatureMap.author_id == author_id).one()
    if not maxSequence:
      maxSequence = 0

    afm = AuthorFeatureMap(author_id, feature_id, maxSequence + 1)

    try:
      self.db_session.add(afm)
      self.db_session.flush()
      log.info("created author/feature link: %s -> %s" % (author_name, feature_name))

    except IntegrityError, e:
      self.request.response.status_int = 409
      return {'error': e.message}

    response = {'author': author_name, 'feature': feature_name}

    return response

  # delete the feature from the author's feature set
  #
  @view_config(route_name='author.features.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteAuthorService(self):

    author_name = self.request.matchdict['authorname']
    feature_name = self.request.matchdict['featurename']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      feature_id, = self.db_session.query(Feature.id).filter_by(name=feature_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature %s' % feature_name}

    try:
      afm = self.db_session.query(AuthorFeatureMap).filter_by(author_id=author_id, feature_id=feature_id).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature for author'}

    self.db_session.delete(afm)

    return {}

  # GET /v1/authors/{authorname}/features/{featurename}
  #
  # get info & configuration details for the author's feature
  #
  @view_config(route_name='author.features.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getAuthorServiceInfo(self):

    author_name = self.request.matchdict['authorname']
    feature_name = self.request.matchdict['featurename']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      serviceId, = self.db_session.query(Feature.id).filter_by(name=feature_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature %s' % feature_name}

    try:
      afm = self.db_session.query(AuthorFeatureMap).filter_by(author_id=author_id, feature_id=serviceId).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature for author'}

    response = {'author': author_name, 'feature': feature_name, 'sequence': afm.sequence}

    return response

  # GET /v1/authors/{authorname}/features/default
  #
  @view_config(route_name='author.features.default', request_method='GET', renderer='jsonp', http_cache=0)
  def getDefaultFeature(self):

    author_name = self.request.matchdict['authorname']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    # it's OK for no default to exists.  The convention if no explicit default exists is to use the first feature
    try:
      feature_name, = self.db_session.query(Feature.name). \
                                    join(AuthorFeatureDefault, Feature.id == AuthorFeatureDefault.feature_id). \
                                    filter(AuthorFeatureDefault.author_id == author_id).one()
    except NoResultFound:
      feature_name = None

    result = {'author': author_name, 'default_feature': feature_name}

    return result

  @view_config(route_name='author.features.default.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def setDefaultFeature(self):

    author_name = self.request.matchdict['authorname']
    feature_name = self.request.matchdict['featurename']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      feature_id, = self.db_session.query(Feature.id).filter_by(name=feature_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown feature %s' % feature_name}

    # if a default already exists then remove it
    try:
      afd = self.db_session.query(AuthorFeatureDefault).filter_by(author_id=author_id).one()
      self.db_session.delete(afd)
    except NoResultFound:
      pass

    afd = AuthorFeatureDefault(author_id, feature_id)
    self.db_session.add(afd)
    self.db_session.flush()

    return {'author': author_name, 'default_feature': feature_name}
