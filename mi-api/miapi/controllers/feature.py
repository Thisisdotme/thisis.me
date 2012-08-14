'''
Created on Apr 24, 2012

@author: howard
'''

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Feature

from tim_commons import db

import miapi.resource

import miapi.json_renders.feature

log = logging.getLogger(__name__)


def add_views(configuration):
  # Features
  configuration.add_view(
      list_features,
      context=miapi.resource.Features,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_feature,
      context=miapi.resource.Features,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # Feature
  configuration.add_view(
      get_feature,
      context=miapi.resource.Feature,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_feature,
      context=miapi.resource.Feature,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)


def list_features(request):

  feature_list = []
  for feature in db.Session().query(Feature).order_by(Feature.name):
    feature_list.append(miapi.json_renders.feature.to_JSON_dictionary(feature, request))

  return {'features': feature_list}


def add_feature(request):

  feature_info = request.json_body

  feature_name = feature_info.get('name')
  if feature_name is None:
    request.response.status_int = 400
    return {'error': 'missing name'}

  feature = Feature(feature_name)

  db_session = db.Session()

  try:
    db_session.add(feature)
    db_session.flush()

    log.info('create feature: {0}'.format(feature_name))

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

  return {'feature': miapi.json_renders.feature.to_JSON_dictionary(feature, request)}


def get_feature(feature_context, request):

  feature = feature_context.feature

  return miapi.json_renders.feature.to_JSON_dictionary(feature, request)


def delete_feature(feature_context, request):

  feature = feature_context.feature

  db_session = db.Session()

  try:
    db_session.delete(feature)
    db_session.flush()
  except Exception, e:
    request.response.status_int = 500
    return {'error': e.message}

  return miapi.json_renders.feature.to_JSON_dictionary(feature, request)
