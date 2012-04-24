'''
Created on Jan 5, 2012

@author: howard
'''
import logging
import json

from datetime import datetime

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Author
from mi_schema.models import Service
from mi_schema.models import AuthorServiceMap

from miapi.models import DBSession

from author_utils import serviceBuild

log = logging.getLogger(__name__)


##
##  author/service relationship
##

class AuthorServiceController(object):
  
  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()


  # GET /v1/authors/{authorname}/services
  #
  # list all services associated with the author
  @view_config(route_name='author.services', request_method='GET', renderer='jsonp', http_cache=0)
  def listAuthorServices(self):
  
    authorName = self.request.matchdict['authorname']
  
    dbsession = DBSession()
  
    try:
      authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    services = []
    for service in dbsession.query(Service).join(AuthorServiceMap).filter(Service.id==AuthorServiceMap.service_id).join(Author).filter(AuthorServiceMap.author_id==authorId).order_by(Service.service_name):
      services.append({'service_id':service.id,
                       'name':service.service_name,
                       'color_icon_high_res':self.request.static_url('miapi:%s' % service.color_icon_high_res),
                       'color_icon_medium_res':self.request.static_url('miapi:%s' % service.color_icon_medium_res),
                       'color_icon_low_res':self.request.static_url('miapi:%s' % service.color_icon_low_res),
                       'mono_icon_high_res':self.request.static_url('miapi:%s' % service.mono_icon_high_res),
                       'mono_icon_medium_res':self.request.static_url('miapi:%s' % service.mono_icon_medium_res),
                       'mono_icon_low_res':self.request.static_url('miapi:%s' % service.mono_icon_low_res)})
  
    return {'author_name':authorName,'services':services}
  

  # GET /v1/authors/{authorname}/services/{servicename}
  # 
  # get info & configuration details for the author's service
  #
  @view_config(route_name='author.services.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getAuthorServiceInfo(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
  
    dbsession = DBSession()
  
    try:
      authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      serviceId, = dbsession.query(Service.id).filter_by(service_name=serviceName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown service %s' % serviceName}
  
    try:
      afm = dbsession.query(AuthorServiceMap).filter_by(author_id=authorId,service_id=serviceId).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown service for author'}
    
    response = {'author':authorName,'service':serviceName,'last_update_time': datetime.isoformat(afm.last_update_time) if afm.last_update_time else None}
  
    if afm.access_token:
      response['access_token'] = afm.access_token
  
    if afm.access_token_secret:
      response['access_token_secret'] = afm.access_token_secret
  
    if afm.auxillary_data:
      response['auxillary_data'] = json.loads(afm.auxillary_data)
  
    return response


  # PUT /v1/authors/{authorname}/services/{servicename}
  #
  # add the service to the author's service set
  #
  @view_config(route_name='author.services.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def putAuthorService(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
  
    credentials = self.request.json_body
    accessToken = credentials.get('access_token')
    accessTokenSecret = credentials.get('access_token_secret')
  
    # check for auxillary data and convert to a string if it exists
    auxillaryData = credentials.get('auxillary_data')
    if auxillaryData:
      auxillaryData = json.dumps(auxillaryData)
    
    dbsession = DBSession()
  
    try:
      authorId, = dbsession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    try:
      serviceId, = dbsession.query(Service.id).filter_by(service_name=serviceName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown service %s' % serviceName}
  
    authorFeatureMap = AuthorServiceMap(authorId,serviceId,accessToken,accessTokenSecret,auxillaryData)
  
    try:
      dbsession.add(authorFeatureMap)
      dbsession.commit()
      log.info("created author/service link: %s -> %s" % (authorName,serviceName))
  
    except IntegrityError, e:
      dbsession.rollback()
      self.request.response.status_int = 409
      return {'error':e.message}
  
    # load events for this service
    s3Bucket = self.request.registry.settings.get('mi.s3_bucket')
    awsAccessKey = self.request.registry.settings.get('mi.aws_access_key')
    awsSecretKey = self.request.registry.settings.get('mi.aws_secret_key')
    serviceBuild(authorName,serviceName,False,s3Bucket,awsAccessKey,awsSecretKey)
  
    response = {'author':authorName,'service':serviceName}
  
    if accessToken:
      response['access_token'] = accessToken
  
    if accessTokenSecret:
      response['access_token_secret'] = accessTokenSecret
      
    if auxillaryData:
      response['auxillary_data'] = json.loads(auxillaryData)
    
    dbsession.close()
  
    return response


  # delete the service from the author's service set
  #
  @view_config(route_name='author.services.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteAuthorService(self):
  
    authorname = self.request.matchdict['authorname']
    servicename = self.request.matchdict['servicename']
  
    dbsession = DBSession()
  
    author = dbsession.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error':'unknown authorname'}
  
    service = dbsession.query(Service).filter_by(service_name=servicename).first()
    if service == None:
      self.request.response.status_int = 404
      return {'error':'unknown service'}
  
    authorFeatureMap = dbsession.query(AuthorServiceMap).filter_by(author_id=author.id,service_id=service.id).first()
    if not authorFeatureMap:
      self.request.response.status_int = 404
      return {'error':'unknown service for author'}
  
    try:
      dbsession.delete(authorFeatureMap)
      dbsession.commit()
    
    except Exception:
      dbsession.rollback();
      raise
  
    return {}

