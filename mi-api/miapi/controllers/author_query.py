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
  author = events_context.author

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  # get the query parameters
  since_date, since_service_id, since_event_id = miapi.controllers.parse_page_param(
      request.params.get('since'))
  until_date, until_service_id, until_event_id = miapi.controllers.parse_page_param(
      request.params.get('until'))

  max_page_limit = miapi.tim_config['api']['max_page_limi']
  page_limit = min(request.params.get('count', max_page_limit), max_page_limit)

  event_rows = data_access.service_event.query_service_events_page(
      author.id,
      page_limit,
      since_date=since_date,
      since_service_id=since_service_id,
      since_event_id=since_event_id,
      until_date=until_date,
      until_service_id=until_service_id,
      until_event_id=until_event_id)

  prev_link = None
  next_link = None
  events = []
  for event in event_rows:
    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author.id,
        event.service_id)

    event_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        event,
        me_asm,
        asm,
        author)
    if event_obj:
      events.append(event_obj)

      param_value = miapi.controllers.create_page_param(
          event.create_time,
          event.service_id,
          event.event_id)

      if prev_link is None:
        prev_link = request.resource_url(
            events_context,
            query={'since': param_value, 'count': page_limit})
      next_link = request.resource_url(
          events_context,
          query={'until': param_value, 'count': page_limit})

  return {'entries': events,
          'paging': {'prev': prev_link, 'next': next_link}}


def get_event_detail(event_context, request):
  author = event_context.author
  event = event_context.event

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      event.service_id)

  return miapi.controllers.author_utils.createServiceEvent(
      request,
      event,
      me_asm,
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

  # NOTE: this method doesn't exist anymore. use get_service_author_fragment
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
