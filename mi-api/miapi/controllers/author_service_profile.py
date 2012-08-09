from mi_schema.models import AuthorServiceMap
from profile_fetchers import profile_fetcher
from data_access import service

import tim_commons.db
import miapi.resource
import data_access.author


def add_views(configuration):
  configuration.add_view(
    get_profile,
    context=miapi.resource.Author,
    name='profile',
    request_method='GET',
    permission='read',
    renderer='jsonp',
    http_cache=0)

  configuration.add_view(
    get_service_profile,
    context=miapi.resource.AuthorService,
    name='profile',
    request_method='GET',
    permission='read',
    renderer='jsonp',
    http_cache=0)


def get_profile(author_context, request):
  author_id = author_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  # service profile precedence is: linkedin, facebook, googleplus, twitter, instagram, foursquare
  # get all service mappings for author
  mappings = {}
  for asm in tim_commons.db.Session().query(AuthorServiceMap).filter_by(author_id=author_id).all():
    mappings[asm.service_id] = asm

  profile_json = None

  for service_name in ['linkedin', 'facebook', 'googleplus', 'twitter', 'instagram', 'foursquare']:
    asm = mappings.get(service.name_to_service[service_name].id)
    if asm:
      fetcher = profile_fetcher.from_service_name(service_name, miapi.oauth_config[service_name])
      profile_json = fetcher.get_author_profile(asm.service_author_id, asm)
      break

  return profile_json


def get_service_profile(author_service_context, request):
  author_id = author_service_context.author_id

  author = data_access.author.query_author(author_id)
  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  service = data_access.service.name_to_service.get(author_service_context.service_name)
  if service is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown service %s' % author_service_context.service_name}

  fetcher = profile_fetcher.from_service_name(
      service.service_name,
      miapi.oauth_config[service.service_name])
  if not fetcher:
    request.response.status_int = 404
    return {'error': 'profile information is not available for service %s' % service.service_name}

  try:
    mapping = tim_commons.db.Session().query(AuthorServiceMap). \
              filter_by(service_id=service.id, author_id=author_id).one()
  except:
    request.response.status_int = 404
    return {'error': 'unknown service for author'}

  profile_json = fetcher.get_author_profile(mapping.service_author_id, mapping)

  return profile_json
