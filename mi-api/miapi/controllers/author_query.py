'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config
from sqlalchemy import (and_)

from tim_commons import db

from mi_schema.models import (Author, Service, ServiceEvent, AuthorServiceMap, Highlight)

from miapi.globals import LIMIT

from author_utils import createServiceEvent, createHighlightEvent

log = logging.getLogger(__name__)


##
## author ServiceEvents functionality
##

class AuthorQueryController(object):
  '''
  Constructor
  '''

  def __init__(self, request):
      self.request = request
      self.db_session = db.Session()

  # GET /v1/authors/{authorname}/highlights
  #
  # get the event highlights for the author
  #
  @view_config(route_name='author.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  def getHighlights(self):

    authorName = self.request.matchdict['authorname']

    # get author-id for authorName
    try:
      authorId, = self.db_session.query(Author.id).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    events = []
    for highlight, event, asm, author, serviceName in self.db_session.query(Highlight, ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
              join(ServiceEvent, Highlight.service_event_id == ServiceEvent.id). \
              join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
              join(Author, AuthorServiceMap.author_id == Author.id). \
              join(Service, AuthorServiceMap.service_id == Service.id). \
              filter(and_(AuthorServiceMap.author_id == authorId, Highlight.weight > 0)). \
              order_by(Highlight.weight.desc(), ServiceEvent.create_time). \
              limit(LIMIT):
      events.append(createHighlightEvent(self.db_session, self.request, highlight, event, asm, author, serviceName))

    return {'events': events, 'paging': {'prev': None, 'next': None}}

  # GET /v1/authors/{authorname}/events
  #
  # get all FeatureEvents for the author (constrained to query arg. filters)
  #
  @view_config(route_name='author.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def getEvents(self):

    authorName = self.request.matchdict['authorname']

    # get author-id for authorName
    try:
      author = self.db_session.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    events = []
    for event, asm in self.db_session.query(ServiceEvent, AuthorServiceMap). \
          join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
          join(Service, AuthorServiceMap.service_id == Service.id). \
          filter(AuthorServiceMap.author_id == author.id). \
          filter(ServiceEvent.correlation_id == None). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(LIMIT):
      event_obj = createServiceEvent(self.db_session, self.request, event, asm, author)
      if event_obj:
        events.append(event_obj)

    return {'events': events, 'paging': {'prev': None, 'next': None}}

  # GET /v1/authors/{authorname}/events/{eventID}
  #
  # get details for the service event
  #
  @view_config(route_name='author.query.events.eventId', request_method='GET', renderer='jsonp', http_cache=0)
  def getEventDetail(self):

    authorName = self.request.matchdict['authorname']
    serviceEventID = int(self.request.matchdict['eventID'])

    # get author-id for authorName
    try:
      author = self.db_session.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}
    try:
      event, asm = self.db_session.query(ServiceEvent, AuthorServiceMap). \
            join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
            filter(ServiceEvent.id == serviceEventID). \
            filter(AuthorServiceMap.author_id == author.id). \
            one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown event id %d' % serviceEventID}

    return {'event': createServiceEvent(self.db_session, self.request, event, asm, author)}

  # GET /v1/authors/{authorname}/topstories
  #
  # get details for the service event
  #
  @view_config(route_name='author.query.topstories', request_method='GET', renderer='jsonp', http_cache=0)
  def getAuthorTopStories(self):

    STORY_LIMIT = 5

    authorName = self.request.matchdict['authorname']

    # get author-id for authorName
    try:
      author = self.db_session.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    events = []
    for event, asm in self.db_session.query(ServiceEvent, AuthorServiceMap). \
          join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
          filter(AuthorServiceMap.author_id == author.id). \
          filter(ServiceEvent.correlation_id == None). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(STORY_LIMIT):
      event_obj = createServiceEvent(self.db_session, self.request, event, asm, author)
      if event_obj:
        events.append(event_obj)

    return {'events': events}
