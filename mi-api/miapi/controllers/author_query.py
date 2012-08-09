import miapi.resource
import miapi.controllers

import data_access.author
import data_access.service_event
import data_access.post_type
import data_access.service
import data_access.author_service_map


def add_views(configuration):
  # Events
  configuration.add_view(
      get_events,
      context=miapi.resource.Events,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)

  # Event
  configuration.add_view(
      get_event_detail,
      context=miapi.resource.Event,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def get_events(events_context, request):
  author_id = events_context.author_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author %s' % author_id}

  author_object = miapi.controllers.get_tim_author_fragment(request, author.author_name)

  # TODO: use paging limit should be configurable
  page_limit = 200

  event_rows = data_access.service_event.query_service_events_descending_time(
      author_id,
      page_limit)
  events = []
  for event in event_rows:
    # filter well-known and instagram photo albums so they don't appear in the timeline
    if (event.type_id == data_access.post_type.label_to_id('photo-album') and
        (event.service_id == data_access.service.name_to_id('me') or
         event.service_id == data_access.service.name_to_id('instagram'))):
      continue

    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author_id,
        event.service_id)

    event_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        event,
        asm,
        author)
    if event_obj:
      events.append(event_obj)

  # TODO: implement the correct result for paging
  return {'author': author_object,
          'events': events,
          'paging': {'prev': None, 'next': None}}


def get_event_detail(event_context, request):
  author_id = event_context.author_id
  event_id = event_context.event_id

  author = data_access.author.query_author(author_id)

  if author is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown author %s' % author_id}

  event_row = data_access.service_event.query_service_event_by_id(author_id, event_id)

  if event_row is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown event id %d' % event_id}

  asm = data_access.author_service_map.query_asm_by_author_and_service(
      author_id,
      event_row.service_id)

  return miapi.controllers.author_utils.createServiceEvent(
      request,
      event_row,
      asm,
      author)


'''
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
            order_by(Highlight.weight.desc(), ServiceEvent.create_time):
    events.append(createHighlightEvent(self.db_session, self.request, highlight, event, asm, author, serviceName))

  return {'author': author_obj,
          'events': events,
          'paging': {'prev': None, 'next': None}}


'''
