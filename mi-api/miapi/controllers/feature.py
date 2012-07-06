'''
Created on Apr 24, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Feature

from tim_commons import db

log = logging.getLogger(__name__)


class FeatureController(object):

  def __init__(self, request):
    '''
    Constructor
    '''
    self.request = request
    self.db_session = db.Session()

  @view_config(route_name='features', request_method='GET', renderer='jsonp', http_cache=0)
  def listFeatures(self):

    featureList = []
    for feature in self.db_session.query(Feature).order_by(Feature.name):
      featureList.append(feature.toJSONObject())

    return {'features': featureList}

  @view_config(route_name='feature.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def addFeature(self):

    featureName = self.request.matchdict['featurename']

    feature = Feature(featureName)

    try:
      self.db_session.add(feature)
      self.db_session.flush()

      log.info("create feature: %(featurename)s" % {'featurename': featureName})

    except IntegrityError, e:
      self.request.response.status_int = 409
      return {'error': e.message}

    return {'service': feature.toJSONObject()}

  @view_config(route_name='feature.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteFeature(self):

    featureName = self.request.matchdict['featurename']

    try:
      feature = self.db_session.query(Feature).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'feature "%s" does not exist' % featureName}

    self.db_session.delete(feature)

    return {}

  @view_config(route_name='feature.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getFeature(self):

    featureName = self.request.matchdict['featurename']

    try:
      feature = self.db_session.query(Feature).filter_by(name=featureName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'feature "%s" does not exist' % featureName}

    return feature.toJSONObject()
