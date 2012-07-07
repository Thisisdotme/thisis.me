import logging
import urllib2
import json

from pyramid.view import view_config

from tim_commons import request_with_method

log = logging.getLogger(__name__)

@view_config(route_name='supported_features', request_method='GET', renderer='timweb:templates/supported_features.pt')
def supported_features(request):
  try:
    req = request_with_method.RequestWithMethod('http://%s/v1/features' % request.registry.settings['mi.api.endpoint'], 'GET')
    res = urllib2.urlopen(req)
    resJSON = json.loads(res.read())
  except Exception, e:
    log.error(e)
  
  return {'features':resJSON['features']}
