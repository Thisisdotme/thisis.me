from tim_commons import db

import data_access.service
import data_access.author_service_map

from mi_schema.models import Author, AuthorGroupMap, ServiceEvent, AuthorServiceMap, ServiceObjectType

from author_utils import createServiceEvent

import miapi.resource


def add_views(configuration):
  # AuthorGroupEvents
  configuration.add_view(
      list_group_events,
      context=miapi.resource.AuthorGroupEvents,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
'''
  # AuthorGroupHighlights
  configuration.add_view(
      list_group_highlights,
      context=miapi.resource.AuthorGroupHighlights,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
'''


# /v1/authors/{authorname}/groups/{groupname}/events
#
# get all events for the author's group
#
def list_group_events(context, request):

  author = context.author
  author_group = context.author_group

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  db_session = db.Session()

  events = []
  for event, asm, author in db_session. \
          query(ServiceEvent, AuthorServiceMap, Author). \
          join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
          join(AuthorGroupMap, AuthorServiceMap.author_id == AuthorGroupMap.author_id). \
          join(Author, AuthorServiceMap.author_id == Author.id). \
          filter(AuthorGroupMap.author_group_id == author_group.id). \
          filter(ServiceEvent.correlation_id == None). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(200):

    ''' filter well-known and instagram photo albums so they
        don't appear in the timeline
    '''
    if (event.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and
        (event.service_id == data_access.service.name_to_id('me') or
         event.service_id == data_access.service.name_to_id('instagram'))):
      continue

    event_obj = createServiceEvent(request, event, me_asm, asm, author)
    if event_obj:
      events.append(event_obj)

  return {'events': events, 'paging': {'prev': None, 'next': None}}


'''
# GET /v1/authors/{authorname}/groups/{groupname}/highlights
#
# get the highlights for the author's group
#
def list_group_highlights(context, request):

  author = context.author
  author_group = context.author_group

  db_session = db.Session()

  events = []
  for highlight, event, asm, author, serviceName in db_session.query(Highlight, ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
            join(ServiceEvent, Highlight.service_event_id == ServiceEvent.id). \
            join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
            join(AuthorGroupMap, AuthorServiceMap.author_id == AuthorGroupMap.author_id). \
            join(Author, AuthorServiceMap.author_id == Author.id). \
            join(Service, AuthorServiceMap.service_id == Service.id). \
            filter(and_(AuthorGroupMap.author_group_id == author_group.id, Highlight.weight > 0)). \
            order_by(Highlight.weight.desc(), ServiceEvent.create_time):
    events.append(createHighlightEvent(db_session, request, highlight, event, asm, author, serviceName))

  return {'events': events, 'paging': {'prev': None, 'next': None}}
'''
