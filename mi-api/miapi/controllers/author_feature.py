import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func


from mi_schema.models import Feature, AuthorFeatureMap, AuthorFeatureDefault

from .feature_utils import getAuthorFeatures
import miapi.resource
import data_access.author
import tim_commons.db


def add_views(configuration):
  # Author Features
  configuration.add_view(
      list_author_features,
      context=miapi.resource.AuthorFeatures,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
    add_author_feature,
    context=miapi.resource.AuthorFeatures,
    request_method='POST',
    permission='create',
    renderer='jsonp',
    http_cache=0)
  configuration.add_view(
    get_default_feature,
    context=miapi.resource.AuthorFeatures,
    name='default',
    request_method='GET',
    permission='read',
    renderer='jsonp',
    http_cache=0)
  configuration.add_view(
    set_default_feature,
    context=miapi.resource.AuthorFeatures,
    name='default',
    request_method='PUT',
    permission='write',
    renderer='jsonp',
    http_cache=0)

  # Author Feature
  configuration.add_view(
      delete_author_feature,
      context=miapi.resource.AuthorFeature,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      get_author_service_info,
      context=miapi.resource.AuthorFeature,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def list_author_features(author_features_context, request):
  author_id = author_features_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  features = getAuthorFeatures(tim_commons.db.Session(), author_id)

  return {'author_name': author.author_name, 'features': features}


def add_author_feature(author_features_context, request):
  author_id = author_features_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  feature_name = request.json_body['feature_name']

  feature = Feature.query_by_name(feature_name)
  if feature is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown feature %s' % feature_name}

  # get the max feature sequence for this author
  maxSequence, = tim_commons.db.Session().query(func.max(AuthorFeatureMap.sequence)). \
                 filter(AuthorFeatureMap.author_id == author_id).one()
  if not maxSequence:
    maxSequence = 0

  afm = AuthorFeatureMap(author_id, feature.id, maxSequence + 1)

  try:
    tim_commons.db.Session().add(afm)
    tim_commons.db.Session().flush()
    logging.info("created author/feature link: %s -> %s", author.author_name, feature_name)

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

  response = {'author': author.author_name, 'feature': feature_name}

  return response


def delete_author_feature(author_feature_context, request):
  author_id = author_feature_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  feature_name = author_feature_context.feature_name

  feature = Feature.query_by_name(feature_name)
  if feature is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown feature %s' % feature_name}

  try:
    afm = tim_commons.db.Session().query(AuthorFeatureMap). \
          filter_by(author_id=author_id, feature_id=feature.id).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error': 'unknown feature for author'}

  tim_commons.db.Session().delete(afm)
  tim_commons.db.Session().flush()

  return {}


def get_author_service_info(author_feature_context, request):
  author_id = author_feature_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  feature_name = author_feature_context.feature_name

  feature = Feature.query_by_name(feature_name)
  if feature is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown feature %s' % feature_name}

  try:
    afm = tim_commons.db.Session().query(AuthorFeatureMap). \
          filter_by(author_id=author_id, feature_id=feature.id).one()
  except NoResultFound:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown feature for author'}

  response = {'author': author.author_name, 'feature': feature_name, 'sequence': afm.sequence}

  return response


def get_default_feature(author_features_context, request):
  author_id = author_features_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  # it's OK for no default to exists. The convention if no explicit default exists is to use the
  # first feature
  try:
    feature_name, = tim_commons.db.Session().query(Feature.name). \
                    join(AuthorFeatureDefault, Feature.id == AuthorFeatureDefault.feature_id). \
                    filter(AuthorFeatureDefault.author_id == author_id).one()
  except NoResultFound:
    feature_name = None

  result = {'author': author.author_name, 'default_feature': feature_name}

  return result


def set_default_feature(author_features_context, request):
  author_id = author_features_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  feature_name = request.json_body['default_feature']

  feature = Feature.query_by_name(feature_name)
  if feature is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown feature %s' % feature_name}

  # if a default already exists then remove it
  try:
    afd = tim_commons.db.Session().query(AuthorFeatureDefault).filter_by(author_id=author_id).one()
    tim_commons.db.Session().delete(afd)
  except NoResultFound:
    pass

  afd = AuthorFeatureDefault(author_id, feature.id)
  tim_commons.db.Session().add(afd)
  tim_commons.db.Session().flush()

  return {'author': author.author_name, 'default_feature': feature_name}
