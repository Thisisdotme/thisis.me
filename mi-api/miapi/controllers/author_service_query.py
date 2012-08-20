from author_utils import createServiceEvent
import miapi.resource
import data_access.service
import data_access.service_event


def add_views(configuration):
  configuration.add_view(
      get_events,
      context=miapi.resource.AuthorService,
      name='events',
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def get_events(author_service_context, request):
  author = author_service_context.author
  asm = author_service_context.author_service_map

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  # get the query parameters
  since_date, since_service_id, since_event_id = miapi.controllers.parse_page_param(
      request.params.get('since'))
  until_date, until_service_id, until_event_id = miapi.controllers.parse_page_param(
      request.params.get('until'))

  max_page_limit = miapi.tim_config['api']['max_page_limit']
  page_limit = min(request.params.get('count', max_page_limit), max_page_limit)

  service_events = data_access.service_event.query_service_events_page_by_service(
      author.id,
      asm.service_id,
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
  for service_event in service_events:
    event_obj = createServiceEvent(request, service_event, me_asm, asm, author)
    if event_obj:
      events.append(event_obj)

      param_value = miapi.controllers.create_page_param(
          service_event.create_time,
          service_event.service_id,
          service_event.event_id)

      if prev_link is None:
        prev_link = request.resource_url(
            author_service_context,
            query={'since': param_value, 'count': page_limit})
      next_link = request.resource_url(
          author_service_context,
          query={'until': param_value, 'count': page_limit})

  return {'entries': events,
          'paging': {'prev': prev_link, 'next': next_link}}
