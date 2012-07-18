'''
Created on Feb 22, 2012

@author: howard
'''
import logging

from sqlalchemy import (and_)

from pyramid.view import view_config

from tim_commons import db

from data_access import service

from mi_schema.models import Author, Service, AuthorServiceMap, ServiceEvent, ServiceObjectType

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
      self.db_session = db.Session()

  # GET /v1/authors/{authorname}/services/{servicename}/highlights
  #
  # return highlights for the service
  #
  @view_config(route_name='author.services.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  def getHighlights(self):

    return {'error': 'not implemented'}

  # GET /v1/authors/{authorname}/services/{servicename}/events'
  #
  # get all the serviceEvents for the author and service
  #
  @view_config(route_name='author.services.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def get_events(self):

    author_name = self.request.matchdict['authorname']
    service_name = self.request.matchdict['servicename']

    # get author-id for author_name
    try:
      author = self.db_session.query(Author).filter(Author.author_name == author_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author {0}'.format(author_name)}

    # get service-id for service_name
    try:
      serviceId = self.db_session.query(Service.id).filter(Service.service_name == service_name).scalar()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown service {0}'.format(author_name)}

    events = []
    for event, asm in self.db_session.query(ServiceEvent, AuthorServiceMap). \
                    join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
                    filter(and_(AuthorServiceMap.service_id == serviceId,
                                AuthorServiceMap.author_id == author.id)). \
                    filter(ServiceEvent.correlation_id == None). \
                    order_by(ServiceEvent.create_time.desc()). \
                    limit(LIMIT):

      ''' filter well-known and instagram photo albums so they
          don't appear in the timeline
      '''
      if (event.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and
          (event.service_id == service.name_to_id('me') or
           event.service_id == service.name_to_id('instagram'))):
        continue

      event_obj = createServiceEvent(self.db_session, self.request, event, asm, author)
      if event_obj:
        events.append(event_obj)

    return {'events': events, 'paging': {'prev': None, 'next': None}}
