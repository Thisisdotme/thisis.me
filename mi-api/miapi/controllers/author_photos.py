import miapi.controllers.author_utils
import miapi.resource
import data_access.service_event


def add_views(configuration):
  configuration.add_view(
      get_photos,
      context=miapi.resource.Photos,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)


def get_photos(photos_context, request):
  author = photos_context.author
  album = photos_context.album

  me_asm = data_access.author_service_map.query_asm_by_author_and_service(
      author.id,
      data_access.service.name_to_id('me'))

  page_limit = min(int(request.params.get('count', miapi.tim_config['api']['default_page_limit'])),
                   int(miapi.tim_config['api']['max_page_limit']))

  # get the query parameters
  since_date, since_service_id, since_event_id = miapi.controllers.parse_page_param(
      request.params.get('since'))
  until_date, until_service_id, until_event_id = miapi.controllers.parse_page_param(
      request.params.get('until'))

  photo_events = data_access.service_event.query_photos_page(
      author.id,
      album.event_id,
      album.service_id,
      page_limit,
      since_date=since_date,
      since_service_id=since_service_id,
      since_event_id=since_event_id,
      until_date=until_date,
      until_service_id=until_service_id,
      until_event_id=until_event_id)

  prev_link = None
  next_link = None
  photos = []
  for photo_event in photo_events:
    asm = data_access.author_service_map.query_asm_by_author_and_service(
        author.id,
        photo_event.service_id)

    photo = miapi.controllers.author_utils.createServiceEvent(
        request,
        photo_event,
        me_asm,
        asm,
        author)
    if photo:
      photos.append(photo)

      param_value = miapi.controllers.create_page_param(
          photo_event.create_time,
          photo_event.service_id,
          photo_event.event_id)

      if prev_link is None:
        prev_link = request.resource_url(
            photos_context,
            query={'since': param_value, 'count': page_limit})
      next_link = request.resource_url(
          photos_context,
          query={'until': param_value, 'count': page_limit})

  return {'entries': photos,
          'paging': {'prev': prev_link, 'next': next_link}}
