import logging
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from mi_schema.models import Service, AuthorServiceMap, ServiceObjectType, ServiceEvent
import tim_commons.db
import data_access.service
import miapi.resource


def add_views(configuration):
  # Author Services
  configuration.add_view(
      list_author_services,
      context=miapi.resource.AuthorServices,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_author_service,
      context=miapi.resource.AuthorServices,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # Author Service
  configuration.add_view(
      get_author_service_info,
      context=miapi.resource.AuthorService,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_author_service,
      context=miapi.resource.AuthorService,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)


def list_author_services(author_services_context, request):
  author_id = author_services_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  services = []
  for service in tim_commons.db.Session().query(Service). \
    join(AuthorServiceMap). \
    filter(and_(Service.id == AuthorServiceMap.service_id,
                AuthorServiceMap.author_id == author_id)). \
    order_by(Service.service_name):

    services.append(service.to_JSON_dictionary(request))

  return {'author_name': author.author_name, 'services': services}


def get_author_service_info(author_service_context, request):
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

  asm = data_access.author_service_map.query_asm_by_author_and_service(author_id, service.id)
  if asm is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown service for author'}

  response = {'author': author.author_name,
              'service': service.service_name,
              'last_update_time': datetime.isoformat(asm.last_update_time) if asm.last_update_time else None}

  return response


def add_author_service(author_services_context, request):
  author_id = author_services_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author: %s' % author_id}

  payload = request.json_body
  service_name = payload.get('name')
  accessToken = payload.get('access_token')
  accessTokenSecret = payload.get('access_token_secret')
  service_author_id = payload.get('service_author_id')

  service = data_access.service.name_to_service.get(service_name)
  if service is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown service %s' % service_name}

  author_service_map = AuthorServiceMap(
      author_id,
      service.id,
      accessToken,
      accessTokenSecret,
      service_author_id)

  try:
    tim_commons.db.Session().add(author_service_map)
    tim_commons.db.Session().flush()

    # if this is instagram add an instagram photo album
    if service.id == data_access.service.name_to_id('instagram'):
      instagram__album = ServiceEvent(
          author_service_map.id,
          ServiceObjectType.PHOTO_ALBUM_TYPE,
          author_id,
          service.id,
          '_{0}@{1}'.format(service.service_name, author_id),
          datetime.now(),
          None,
          None,
          'Photos from Instagram')
      tim_commons.db.Session().add(instagram__album)
      tim_commons.db.Session().flush()

    logging.info("created author/service link: %s -> %s", author.author_name, service.service_name)

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

    response = {'author': author.author_name, 'service': service.service_name}

    if accessToken:
      response['access_token'] = accessToken

    if accessTokenSecret:
      response['access_token_secret'] = accessTokenSecret

    if service_author_id:
      response['service_author_id'] = service_author_id

    return response


def delete_author_service(author_service_context, request):
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

  asm = data_access.author_service_map.query_asm_by_author_and_service(author_id, service.id)
  if asm is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown service for author'}

  tim_commons.db.Session().delete(asm)
  tim_commons.db.Session().flush()
  # TODO: should we delete all the service events?

  return {}
