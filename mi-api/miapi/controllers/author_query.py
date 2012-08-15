import datetime
import calendar

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

  # get the query parameters
  since_date, since_service_id, since_event_id = parse_page_param(request.params.get('since'))
  until_date, until_service_id, until_event_id = parse_page_param(request.params.get('until'))

  max_page_limit = miapi.tim_config['api']['max_page_limi']
  page_limit = min(request.params.get('count', max_page_limit), max_page_limit)

  event_rows = data_access.service_event.query_service_events_page(
      author_id,
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
        author_id,
        event.service_id)

    event_obj = miapi.controllers.author_utils.createServiceEvent(
        request,
        event,
        asm,
        author)
    if event_obj:
      events.append(event_obj)

      param_value = create_page_param(event.create_time, event.service_id, event.event_id)

      if prev_link is None:
        prev_link = request.resource_url(events_context, query={'since': param_value})
      next_link = request.resource_url(events_context, query={'until': param_value})

  return {'entries': events,
          'paging': {'prev': prev_link, 'next': next_link}}


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


def create_page_param(date, service_id, event_id):
  return '{0}_{1}_{2}'.format(calendar.timegm(date.utctimetuple()), service_id, event_id)


def parse_page_param(param):
  if param is None:
    return (None, None, None)

  split_param = param.split('_')
  return (
      datetime.datetime.utcfromtimestamp(int(split_param[0])),
      int(split_param[1]),
      '_'.join(split_param[2:]))
