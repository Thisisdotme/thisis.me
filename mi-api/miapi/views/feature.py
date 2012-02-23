'''
Created on Dec, 2011

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError

from mi_schema.models import Feature

from miapi.models import DBSession

log = logging.getLogger(__name__)


# GET /v1/features
#
# return info on all features
@view_config(route_name='features', request_method='GET', renderer='jsonp', permission='admin', http_cache=0)
def features(request):

  dbsession = DBSession()
  features = dbsession.query(Feature)
  featureList = []
  for feature in dbsession.query(Feature).order_by(Feature.feature_name):
    featureList.append({'feature_id':feature.id,
                        'name':feature.feature_name,
                        'color_icon_high_res':request.static_url('miapi:%s' % feature.color_icon_high_res),
                        'color_icon_medium_res':request.static_url('miapi:%s' % feature.color_icon_medium_res),
                        'color_icon_low_res':request.static_url('miapi:%s' % feature.color_icon_low_res),
                        'mono_icon_high_res':request.static_url('miapi:%s' % feature.mono_icon_high_res),
                        'mono_icon_medium_res':request.static_url('miapi:%s' % feature.mono_icon_medium_res),
                        'mono_icon_low_res':request.static_url('miapi:%s' % feature.mono_icon_low_res)})

  return {'features':featureList}


# GET /v1/features/{featurename}
#
# retrieve information about a feature
@view_config(route_name='feature.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def featureGet(request):
  
  featureName = request.matchdict['featurename']
  
  dbsession = DBSession()
  feature = dbsession.query(Feature).filter_by(feature_name=featureName).one()

  return {'feature_id':feature.id,
          'name':feature.feature_name,
          'color_icon_high_res':request.static_url('miapi:%s' % feature.color_icon_high_res),
          'color_icon_medium_res':request.static_url('miapi:%s' % feature.color_icon_medium_res),
          'color_icon_low_res':request.static_url('miapi:%s' % feature.color_icon_low_res),
          'mono_icon_high_res':request.static_url('miapi:%s' % feature.mono_icon_high_res),
          'mono_icon_medium_res':request.static_url('miapi:%s' % feature.mono_icon_medium_res),
          'mono_icon_low_res':request.static_url('miapi:%s' % feature.mono_icon_low_res)}

# PUT /v1/features/{featurename}
#
# add a new feature
@view_config(route_name='feature.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def featurePut(request):

  featureName = request.matchdict['featurename']

  images = request.json_body

  colorHighRes = images.get('color_icon_high_res',None)
  colorMedRes = images.get('color_icon_medium_res',None)
  colorLowRes = images.get('color_icon_low_res',None)
  monoHighRes = images.get('mono_icon_high_res',None)
  monoMedRes = images.get('mono_icon_medium_res',None)
  monoLowRes = images.get('mono_icon_low_res',None)

  dbsession = DBSession()
  feature = Feature(featureName,colorHighRes,colorMedRes,colorLowRes,monoHighRes,monoMedRes,monoLowRes)

  try:
    dbsession.add(feature)
    dbsession.commit()
    log.info("create feature: %(featurename)s" % {'featurename':featureName})

  except IntegrityError, e:
    dbsession.rollback()
    request.response.status_int = 409
    return {'error':e.message}

  feature = dbsession.query(Feature).filter_by(feature_name=featureName).first()

  return {'feature': feature.toJSONObject()}

# delete an existing feature
@view_config(route_name='feature.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def featuresDelete(request):
  log.info("delete feature: %(featurename)s" % request.matchdict)
  return {'request':'DELETE /features/%(featurename)s' % request.matchdict}


@view_config(route_name='feature.bundle', request_method='GET', renderer='jsonp', http_cache=0)
def featureBundle(request):
  return {'request':'/feature/%(featurename)s/bundle' % request.matchdict,'bundle':'%(featurename)s' % request.matchdict}
