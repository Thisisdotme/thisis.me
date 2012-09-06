import miapi.resource
import miapi.controllers

import data_access.service_event
import data_access.service
import data_access.author_service_map
import mi_schema.models


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
  configuration.add_view(
      update_event,
      context=miapi.resource.Event,
      request_method='PATCH',
      permission='write',
      renderer='jsonp',
      http_cache=0)


def get_events(events_context, request):
  author = events_context.author

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  post_type_ids = []
  for post_type_name in request.params.getall('post_type'):
    post_type = data_access.post_type.label_to_post_type.get(post_type_name)
    if post_type:
      post_type_ids.append(post_type.type_id)
    else:
      return miapi.error.http_error(request.response, **miapi.error.BAD_REQUEST)

  service_ids = []
  for service_name in request.params.getall('service_name'):
    service = data_access.service.name_to_service.get(service_name)
    if service:
      service_ids.append(service.id)
    else:
      return miapi.error.http_error(request.response, **miapi.error.BAD_REQUEST)

  # get the query parameters
  since_date, since_service_id, since_event_id = miapi.controllers.parse_page_param(
      request.params.get('since'))
  until_date, until_service_id, until_event_id = miapi.controllers.parse_page_param(
      request.params.get('until'))

  page_limit = min(int(request.params.get('count', miapi.tim_config['api']['default_page_limit'])),
                   int(miapi.tim_config['api']['max_page_limit']))

  event_rows = data_access.service_event.query_service_events_page(
      author.id,
      page_limit,
      post_type_ids=post_type_ids,
      service_ids=service_ids,
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
            query={'since': param_value,
                   'count': page_limit,
                   'post_type': request.params.getall('post_type'),
                   'service_name': request.params.getall('service_name')})
      next_link = request.resource_url(
          events_context,
          query={'until': param_value,
                 'count': page_limit,
                 'post_type': request.params.getall('post_type'),
                 'service_name': request.params.getall('service_name')})

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


def update_event(event_context, request):
  author = event_context.author
  event = event_context.event

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      event.service_id)

  put = request.json_body
  hidden = put.get('hidden')

  if hidden is not None:
    if (hidden is True and
        event.service_id == data_access.service.name_to_id('me') and
        (event.event_id == mi_schema.models.ServiceEvent.make_well_known_service_event_id(
           mi_schema.models.ServiceEvent.ALL_PHOTOS_ID,
           author.id) or
         event.event_id == mi_schema.models.ServiceEvent.make_well_known_service_event_id(
           mi_schema.models.ServiceEvent.OFME_PHOTOS_ID,
           author.id) or
         event.event_id == mi_schema.models.ServiceEvent.make_well_known_service_event_id(
           mi_schema.models.ServiceEvent.LIKED_PHOTOS_ID,
           author.id))):
      # You can't hide well known photo albums
      return miapi.error.http_error(request.response, **miapi.error.UNPROCESSABLE)
    else:
      event.hidden = hidden

  data_access.flush()

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
