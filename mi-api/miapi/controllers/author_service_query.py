from sqlalchemy import (and_)

from mi_schema.models import AuthorServiceMap, ServiceEvent, ServiceObjectType


from author_utils import createServiceEvent
import miapi.resource
import data_access.author
import data_access.service
import tim_commons.db


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

  service = data_access.service.name_to_service.get(author_service_context.service_name)
  if service is None:
    # TODO: better error
    request.response.status_int = 404
    return {'error': 'unknown service %s' % author_service_context.service_name}

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  events = []
  for event, asm in tim_commons.db.Session().query(ServiceEvent, AuthorServiceMap). \
    join(AuthorServiceMap, AuthorServiceMap.id == ServiceEvent.author_service_map_id). \
    filter(and_(AuthorServiceMap.service_id == service.id,
                AuthorServiceMap.author_id == author.id)). \
    filter(ServiceEvent.correlation_id == None). \
    order_by(ServiceEvent.create_time.desc()):

    ''' filter well-known and instagram photo albums so they
        don't appear in the timeline
    '''
    if (event.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and
        (event.service_id == service.name_to_id('me') or
         event.service_id == service.name_to_id('instagram'))):
      continue

    event_obj = createServiceEvent(request, event, me_asm, asm, author)
    if event_obj:
      events.append(event_obj)

  return {'events': events, 'paging': {'prev': None, 'next': None}}
