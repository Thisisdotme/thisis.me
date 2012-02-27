'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession

from author_utils import featureBuild

log = logging.getLogger(__name__)


# GET /v1/authors/{authorname}/features/{featurename}/build
#
# refresh featureEvents for this feature
@view_config(route_name='author.features.build', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatureFullBuild(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']

  s3Bucket = request.registry.settings.get('mi.s3_bucket')
  awsAccessKey = request.registry.settings.get('mi.aws_access_key')
  awsSecretKey = request.registry.settings.get('mi.aws_secret_key')
  featureBuild(authorName,featureName,False,s3Bucket,awsAccessKey,awsSecretKey)

  return {}


# GET /v1/authors/{authorname}/features/{featurename}/update
#
# return all authors that match the specified search criteria
#
@view_config(route_name='author.features.update', request_method='GET', renderer='jsonp', http_cache=0)
def authorFeatureIncrementalBuild(request):

  authorName = request.matchdict['authorname']
  featureName = request.matchdict['featurename']

  s3Bucket = request.registry.settings.get('mi.s3_bucket')
  awsAccessKey = request.registry.settings.get('mi.aws_access_key')
  awsSecretKey = request.registry.settings.get('mi.aws_secret_key')
  featureBuild(authorName,featureName,True,s3Bucket,awsAccessKey,awsSecretKey)

  return {}



