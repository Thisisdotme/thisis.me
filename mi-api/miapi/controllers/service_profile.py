'''
Created on Jan 16, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from mi_schema.models import Service, Author, AuthorServiceMap

from mi_profile_retrieval.profile_retriever_factory import ProfileRetrievalFactory

from miapi.models import DBSession

from miapi import oAuthConfig

log = logging.getLogger(__name__)

class ServiceProfileController(object):
  
  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()
  

  # get all the service events for the author and service
  @view_config(route_name='author.services.profile', request_method='GET', renderer='jsonp', http_cache=0)
  def get_service_profile(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
  
    retriever = ProfileRetrievalFactory.get_retriever_for(serviceName)
    if not retriever:
      self.request.response.status_int = 404
      return {'error':'profile information is not available for service %s' % serviceName}  
      
    # get author-id for authorName
    try:
      author_id, = self.dbSession.query(Author.id).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}  
  
    # get service-id for serviceName
    try:
      serviceId, = self.dbSession.query(Service.id).filter(Service.service_name == serviceName).one()
    except:
      self.request.response.status_int = 404
      return {'error':'unknown service %s' % authorName}  
  
    try:
      mapping = self.dbSession.query(AuthorServiceMap).filter_by(service_id=serviceId,author_id=author_id).one()
    except:
      self.request.response.status_int = 404
      return {'error':'unknown service for author'}
  
    profileJSON = retriever.get_author_profile(mapping,self.dbSession,oAuthConfig.get(serviceName))
  
    self.dbSession.close()
  
    return profileJSON
