'''
Created on Feb 22, 2012

@author: howard
'''
import logging

from sqlalchemy import (and_)

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, Service, AuthorServiceMap, ServiceEvent

from miapi.globals import LIMIT

from author_utils import createServiceEvent

log = logging.getLogger(__name__)

#
# AUTHOR SERVICE QUERY: query for the highlights/details of the specified service and author
#

class AuthorServiceQueryController(object):
  
  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request
      self.dbSession = DBSession()

  # GET /v1/authors/{authorname}/services/{servicename}/highlights
  #
  # return highlights for the service
  #
  def getHighlights(self):
    
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
    
    return {'error':'not implemented'}
  

  # GET /v1/authors/{authorname}/services/{servicename}/events'
  #
  # get all the serviceEvents for the author and service  
  #
  ## THIS NEEDS TO MOVE BACK TO getHighlights WHEN IMPLEMENTED
  @view_config(route_name='author.services.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  ##
  @view_config(route_name='author.services.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def getEvents(self):
  
    authorName = self.request.matchdict['authorname']
    serviceName = self.request.matchdict['servicename']
    
    # get author-id for authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown author %s' % authorName}  
  
    # get service-id for serviceName
    try:
      serviceId, = self.dbSession.query(Service.id).filter(Service.service_name == serviceName).one()
    except:
      self.request.response.status_int = 404;
      return {'error':'unknown service %s' % authorName}  
  
    events = []  
    for event,serviceName in self.dbSession.query(ServiceEvent,Service.service_name).join(AuthorServiceMap,AuthorServiceMap.id==ServiceEvent.author_service_map_id).join(Service,AuthorServiceMap.service_id==Service.id).filter(and_(AuthorServiceMap.service_id==serviceId,AuthorServiceMap.author_id==author.id)).filter(ServiceEvent.parent_id==None).order_by(ServiceEvent.create_time.desc()).limit(LIMIT):
      events.append(createServiceEvent(self.dbSession,self.request,serviceName,author))
  
    return {'events':events,'paging':{'prev':None,'next':None}}
