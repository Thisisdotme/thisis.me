from pyramid.view import view_config
from sqlalchemy import (and_)

from tim_commons import db

from data_access import service

from mi_schema.models import (Author, Service, ServiceEvent, AuthorServiceMap, Highlight, ServiceObjectType)

from miapi.globals import LIMIT

from . import get_tim_author_fragment

from author_utils import createServiceEvent, createHighlightEvent


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
  def get_highlights(self):

    author_name = self.request.matchdict['authorname']

    # get author-id for author_name
    try:
      author_id = self.db_session.query(Author.id).filter(Author.author_name == author_name).scalar()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    author_obj = get_tim_author_fragment(self.request, author_name)

    events = []
    for highlight, event, asm, author, serviceName in self.db_session.query(Highlight, ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
              join(ServiceEvent, Highlight.service_event_id == ServiceEvent.id). \
              join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
              join(Author, AuthorServiceMap.author_id == Author.id). \
              join(Service, AuthorServiceMap.service_id == Service.id). \
              filter(and_(AuthorServiceMap.author_id == author_id, Highlight.weight > 0)). \
              order_by(Highlight.weight.desc(), ServiceEvent.create_time). \
              limit(LIMIT):
      events.append(createHighlightEvent(self.db_session, self.request, highlight, event, asm, author, serviceName))

    return {'author': author_obj,
            'events': events,
            'paging': {'prev': None, 'next': None}}

  # GET /v1/authors/{authorname}/events
  #
  # get all FeatureEvents for the author (constrained to query arg. filters)
  #
  @view_config(route_name='author.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def get_events(self):

    author_name = self.request.matchdict['authorname']

    # get author-id for author_name
    try:
      author = self.db_session.query(Author).filter(Author.author_name == author_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    author_obj = get_tim_author_fragment(self.request, author_name)

    events = []
    for event, asm in self.db_session.query(ServiceEvent, AuthorServiceMap). \
          join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
          filter(AuthorServiceMap.author_id == author.id). \
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

    return {'author': author_obj,
            'events': events,
            'paging': {'prev': None, 'next': None}}

  # GET /v1/authors/{authorname}/events/{eventID}
  #
  # get details for the service event
  #
  @view_config(
      route_name='author.query.events.eventId',
      request_method='GET',
      renderer='jsonp',
      http_cache=0)
  def get_event_detail(self):

    author_name = self.request.matchdict['authorname']
    serviceEventID = int(self.request.matchdict['eventID'])

    # get author-id for author_name
    try:
      author = self.db_session.query(Author).filter(Author.author_name == author_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}
    try:
      event, asm = self.db_session.query(ServiceEvent, AuthorServiceMap). \
            join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
            filter(ServiceEvent.id == serviceEventID). \
            filter(AuthorServiceMap.author_id == author.id). \
            one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown event id %d' % serviceEventID}

    return createServiceEvent(self.db_session, self.request, event, asm, author)

  # GET /v1/authors/{authorname}/topstories
  #
  # get details for the service event
  #
  @view_config(route_name='author.query.topstories', request_method='GET', renderer='jsonp', http_cache=0)
  def get_author_top_stories(self):

    STORY_LIMIT = 5

    author_name = self.request.matchdict['authorname']

    # get author-id for author_name
    try:
      author = self.db_session.query(Author).filter(Author.author_name == author_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    author_obj = get_tim_author_fragment(self.request, author_name)

    events = []
    for event, asm in self.db_session.query(ServiceEvent, AuthorServiceMap). \
          join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
          filter(AuthorServiceMap.author_id == author.id). \
          filter(ServiceEvent.correlation_id == None). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(STORY_LIMIT):

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

    return {'author': author_obj,
            'events': events,
            'paging': {'prev': None, 'next': None}}
