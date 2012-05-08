'''
Created on Dec, 2011

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError

from mi_schema.models import Service

from miapi.models import DBSession

log = logging.getLogger(__name__)


class ServicesController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()

  # GET /v1/accounts
  #
  # return info on all services
  @view_config(route_name='services', request_method='GET', renderer='jsonp', permission='admin', http_cache=0)
  def list_accounts(self):

    serviceList = []
    for service in self.dbSession.query(Service).order_by(Service.service_name):
      serviceList.append({'service_id': service.id,
                          'name': service.service_name,
                          'color_icon_high_res': self.request.static_url('miapi:%s' % service.color_icon_high_res),
                          'color_icon_medium_res': self.request.static_url('miapi:%s' % service.color_icon_medium_res),
                          'color_icon_low_res': self.request.static_url('miapi:%s' % service.color_icon_low_res),
                          'mono_icon_high_res': self.request.static_url('miapi:%s' % service.mono_icon_high_res),
                          'mono_icon_medium_res': self.request.static_url('miapi:%s' % service.mono_icon_medium_res),
                          'mono_icon_low_res': self.request.static_url('miapi:%s' % service.mono_icon_low_res)})

    return {'services': serviceList}

  # retrieve information about a service
  @view_config(route_name='services.CRUD', request_method='GET', renderer='jsonp', permission='admin', http_cache=0)
  def get(self):

    serviceName = self.request.matchdict['servicename']

    service = self.dbSession.query(Service).filter_by(service_name=serviceName).one()

    return {'service_id': service.id,
            'name': service.service_name,
            'color_icon_high_res': self.request.static_url('miapi:%s' % service.color_icon_high_res),
            'color_icon_medium_res': self.request.static_url('miapi:%s' % service.color_icon_medium_res),
            'color_icon_low_res': self.request.static_url('miapi:%s' % service.color_icon_low_res),
            'mono_icon_high_res': self.request.static_url('miapi:%s' % service.mono_icon_high_res),
            'mono_icon_medium_res': self.request.static_url('miapi:%s' % service.mono_icon_medium_res),
            'mono_icon_low_res': self.request.static_url('miapi:%s' % service.mono_icon_low_res)}

  # add a new service
  @view_config(route_name='services.CRUD', request_method='PUT', renderer='jsonp', permission='admin', http_cache=0)
  def put(self):

    serviceName = self.request.matchdict['servicename']

    images = self.request.json_body

    colorHighRes = images.get('color_icon_high_res', None)
    colorMedRes = images.get('color_icon_medium_res', None)
    colorLowRes = images.get('color_icon_low_res', None)
    monoHighRes = images.get('mono_icon_high_res', None)
    monoMedRes = images.get('mono_icon_medium_res', None)
    monoLowRes = images.get('mono_icon_low_res', None)

    service = Service(serviceName, colorHighRes, colorMedRes, colorLowRes, monoHighRes, monoMedRes, monoLowRes)

    try:
      self.dbSession.add(service)
      self.dbSession.commit()
      log.info("create service: %(servicename)s" % {'servicename': serviceName})

    except IntegrityError, e:
      self.dbSession.rollback()
      self.request.response.status_int = 409
      return {'error': e.message}

    service = self.dbSession.query(Service).filter_by(service_name=serviceName).first()

    return {'service': service.toJSONObject()}

  # delete an existing service
  @view_config(route_name='services.CRUD', request_method='DELETE', renderer='jsonp', permission='admin', http_cache=0)
  def delete(self):
    log.info("delete service: %(servicename)s" % self.request.matchdict)
    return {'request': 'DELETE /services/%(servicename)s' % self.request.matchdict}
