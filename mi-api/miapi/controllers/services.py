'''
Created on Dec, 2011

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from mi_schema.models import Service

from tim_commons import db

import miapi.resource


log = logging.getLogger(__name__)


def add_views(configuration):
  # Services
  configuration.add_view(
      list_services,
      context=miapi.resource.Services,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_service,
      context=miapi.resource.Services,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # Service
  configuration.add_view(
      get_service,
      context=miapi.resource.Service,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_service,
      context=miapi.resource.Service,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)


# return info on all services
def list_services(request):

  serviceList = []
  for service in db.Session().query(Service).order_by(Service.service_name):
    serviceList.append(service.to_JSON_dictionary(request))

  return {'services': serviceList}


# retrieve information about a service
def get_service(context, request):

  service_name = context.name

  service = db.Session().query(Service).filter_by(service_name=service_name).one()

  return service.to_JSON_dictionary(request)


# add a new service
def add_service(request):

  service_info = request.json_body

  service_name = service_info.get('name')
  if service_name is None:
    request.response.status_int = 400
    return {'error': 'missing name'}

  colorHighRes = service_info.get('color_icon_high_res', None)
  colorMedRes = service_info.get('color_icon_medium_res', None)
  colorLowRes = service_info.get('color_icon_low_res', None)
  monoHighRes = service_info.get('mono_icon_high_res', None)
  monoMedRes = service_info.get('mono_icon_medium_res', None)
  monoLowRes = service_info.get('mono_icon_low_res', None)

  service = Service(service_name, colorHighRes, colorMedRes, colorLowRes, monoHighRes, monoMedRes, monoLowRes)

  db_session = db.Session()

  try:
    db_session.add(service)
    db_session.flush()

    log.debug('successfully created service: {name}'.format(name=service_name))

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

  return service.to_JSON_dictionary(request)


# delete an existing service
def delete_service(context, request):

  service_name = context.name

  db_session = db.Session()
  try:
    service = db_session.query(Service).filter_by(service_name=service_name).one()
    db_session.delete(service)
    db_session.flush()
  except NoResultFound:
    request.response.status_int = 404
    return {'error': 'service "{0}" does not exist'.format(service_name)}
  except Exception, e:
    request.response.status_int = 500
    return {'error': e.message}

  log.info('successfully deleted service: "{name}"'.format(name=service_name))

  return service.to_JSON_dictionary(request)
