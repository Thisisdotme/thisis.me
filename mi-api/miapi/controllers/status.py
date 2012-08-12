'''
Created on Aug 11, 2012

@author: howard
'''

from time import ctime

import miapi.resource


def add_views(configuration):
  # Services
  configuration.add_view(
      status_get,
      context=miapi.resource.Status,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def status_get(self):
  return {'status': 'ok', 'date': ctime()}
