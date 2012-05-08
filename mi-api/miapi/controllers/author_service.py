'''
Created on Jan 5, 2012

@author: howard
'''
import logging

from datetime import datetime

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Author, Service, AuthorServiceMap

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

    dbSession = DBSession()

    try:
      authorId, = dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    services = []
    for service in dbSession.query(Service). \
                             join(AuthorServiceMap). \
                             filter(Service.id == AuthorServiceMap.service_id). \
                             join(Author). \
                             filter(AuthorServiceMap.author_id == authorId). \
                             order_by(Service.service_name):
      services.append({'service_id': service.id,
                       'name': service.service_name,
                       'color_icon_high_res': self.request.static_url('miapi:%s' % service.color_icon_high_res),
                       'color_icon_medium_res': self.request.static_url('miapi:%s' % service.color_icon_medium_res),
                       'color_icon_low_res': self.request.static_url('miapi:%s' % service.color_icon_low_res),
                       'mono_icon_high_res': self.request.static_url('miapi:%s' % service.mono_icon_high_res),
                       'mono_icon_medium_res': self.request.static_url('miapi:%s' % service.mono_icon_medium_res),
                       'mono_icon_low_res': self.request.static_url('miapi:%s' % service.mono_icon_low_res)})

    return {'author_name': authorName, 'services': services}

  # GET /v1/authors/{authorname}/services/{servicename}
  #
  # get info & configuration details for the author's service
  #
  @view_config(route_name='author.services.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getAuthorServiceInfo(self):

    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']

    dbSession = DBSession()

    try:
      authorId, = dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    try:
      serviceId, = dbSession.query(Service.id).filter_by(service_name=serviceName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown service %s' % serviceName}

    try:
      asm = dbSession.query(AuthorServiceMap).filter_by(author_id=authorId, service_id=serviceId).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown service for author'}

    response = {'author': authorName,
                'service': serviceName,
                'last_update_time': datetime.isoformat(asm.last_update_time) if asm.last_update_time else None}

    if asm.access_token:
      response['access_token'] = asm.access_token

    if asm.access_token_secret:
      response['access_token_secret'] = asm.access_token_secret

    return response

  # PUT /v1/authors/{authorname}/services/{servicename}
  #
  # add the service to the author's service set
  #
  @view_config(route_name='author.services.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def putAuthorService(self):

    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']

    payload = self.request.json_body
    accessToken = payload.get('access_token')
    accessTokenSecret = payload.get('access_token_secret')
    service_author_id = payload.get('service_author_id')

    dbSession = DBSession()

    try:
      authorId, = dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    try:
      serviceId, = dbSession.query(Service.id).filter_by(service_name=serviceName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown service %s' % serviceName}

    authorServiceMap = AuthorServiceMap(authorId, serviceId, accessToken, accessTokenSecret, service_author_id)

    try:
      dbSession.add(authorServiceMap)
      dbSession.commit()
      log.info("created author/service link: %s -> %s" % (authorName, serviceName))

    except IntegrityError, e:
      dbSession.rollback()
      self.request.response.status_int = 409
      return {'error': e.message}

    # load events for this service
    s3Bucket = self.request.registry.settings.get('mi.s3_bucket')
    awsAccessKey = self.request.registry.settings.get('mi.aws_access_key')
    awsSecretKey = self.request.registry.settings.get('mi.aws_secret_key')
    serviceBuild(authorName, serviceName, False, s3Bucket, awsAccessKey, awsSecretKey)

    response = {'author': authorName, 'service': serviceName}

    if accessToken:
      response['access_token'] = accessToken

    if accessTokenSecret:
      response['access_token_secret'] = accessTokenSecret

    if service_author_id:
      response['service_author_id'] = service_author_id

    dbSession.close()

    return response

  # delete the service from the author's service set
  #
  @view_config(route_name='author.services.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteAuthorService(self):

    authorname = self.request.matchdict['authorname']
    servicename = self.request.matchdict['servicename']

    author = self.dbSession.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error': 'unknown authorname'}

    service = self.dbSession.query(Service).filter_by(service_name=servicename).first()
    if service == None:
      self.request.response.status_int = 404
      return {'error': 'unknown service'}

    authorServiceMap = self.dbSession.query(AuthorServiceMap).filter_by(author_id=author.id, service_id=service.id).first()
    if not authorServiceMap:
      self.request.response.status_int = 404
      return {'error': 'unknown service for author'}

    try:
      self.dbSession.delete(authorServiceMap)
      self.dbSession.commit()

    except Exception:
      self.dbSession.rollback()
      raise

    return {}
