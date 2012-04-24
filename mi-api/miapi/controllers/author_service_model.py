'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from author_utils import serviceBuild

log = logging.getLogger(__name__)


class AuthorServiceModelController(object):
  
  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request

  
  # GET /v1/authors/{authorname}/services/{servicename}/build
  #
  # refresh serviceEvents for this service
  @view_config(route_name='author.services.build', request_method='GET', renderer='jsonp', http_cache=0)
  def authorServiceFullBuild(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
  
    s3Bucket = self.request.registry.settings.get('mi.s3_bucket')
    awsAccessKey = self.request.registry.settings.get('mi.aws_access_key')
    awsSecretKey = self.request.registry.settings.get('mi.aws_secret_key')
    serviceBuild(authorName,serviceName,False,s3Bucket,awsAccessKey,awsSecretKey)
  
    return {}


  # GET /v1/authors/{authorname}/services/{servicename}/update
  #
  # return all authors that match the specified search criteria
  #
  @view_config(route_name='author.services.update', request_method='GET', renderer='jsonp', http_cache=0)
  def authorServiceIncrementalBuild(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
  
    s3Bucket = self.request.registry.settings.get('mi.s3_bucket')
    awsAccessKey = self.request.registry.settings.get('mi.aws_access_key')
    awsSecretKey = self.request.registry.settings.get('mi.aws_secret_key')
    serviceBuild(authorName,serviceName,True,s3Bucket,awsAccessKey,awsSecretKey)
  
    return {}



