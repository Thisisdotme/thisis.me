import logging
import sys
import calendar

from sqlalchemy import func, and_

from tim_commons.json_serializer import load_string

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service, Relationship, AuthorServiceMap

from miapi import service_object_type_dict

log = logging.getLogger(__name__)


def get_author_info(request, asm, author):

  profile_image_url = asm.profile_image_url if asm.profile_image_url else request.static_url('miapi:%s' % 'img/profile_placeholder.png')

  author_obj = {'profile_image_url': profile_image_url, 'name': author.author_name, 'full_name': author.full_name}

  return author_obj


def get_shared_services(db_session, request, se_id, service_name):

  service_items = [{'service_name':service_name, 'service_image_url':request.static_url('miapi:img/l/services/color/%s.png' % service_name)}]

  # determine all the shared sources -- all service_event rows whose parent_id is this service_event
  for shared_service_name in db_session.query(Service.service_name). \
                                        join(ServiceEvent, ServiceEvent.service_id == ServiceEvent.id). \
                                        filter(ServiceEvent.parent_id == se_id).all():
    service_items.append({'service_name': shared_service_name, 'service_image_url': request.static_url('miapi:img/l/services/color_by_fn/%s.png' % shared_service_name)})

  return service_items


def get_album_name(event):

  well_known_albums = {ServiceEvent.ALL_PHOTOS_ID: 'All Photos',
                       ServiceEvent.OFME_PHOTOS_ID: 'Photos of Me',
                       ServiceEvent.LIKED_PHOTOS_ID: 'Photos I Like'}

  return well_known_albums[event.event_id[:event.event_id.index('@')]] if event.service_id == Service.ME_ID else event.caption


def get_album_count(db_session, se, author):
  # check for the special well-known album "all photos"
  if se.event_id.startswith(ServiceEvent.ALL_PHOTOS_ID):
    count = db_session.query(func.count(ServiceEvent.id)). \
                       filter(and_(ServiceEvent.author_id == author.id,
                                   ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                       scalar()
  else:
    count = db_session.query(func.count(Relationship.child_service_event_id)). \
                       filter(and_(Relationship.parent_author_id == author.id,
                                   Relationship.parent_service_id == se.service_id, \
                                   Relationship.parent_service_event_id == se.event_id)). \
                       scalar()
  return count


def make_photo_album_obj(db_session, request, se, asm, author, service_name):
  count = get_album_count(db_session, se, author)
  if count > 0:
    album = {'type': service_object_type_dict[ServiceObjectType.PHOTO_ALBUM_TYPE],
              'id': se.id,
              'create_time': calendar.timegm(se.create_time.timetuple()),
              'headline': get_album_name(se),
              'author': get_author_info(request, asm, author),
              'service_name': service_name,
              'count': count}
  else:
    album = None

  return album


def make_photo_obj(db_session, request, se, asm, author, service_name):

  services = get_shared_services(db_session, request, se.id, service_name)

  photo = {'type': service_object_type_dict[ServiceObjectType.PHOTO_TYPE],
           'id': se.id,
           'create_time': calendar.timegm(se.create_time.timetuple()),
           'author': get_author_info(request, asm, author),
           'link': request.route_url('author.query.events.eventId', authorname=author.author_name, eventID=se.id),
           'service': service_name,
           'sources': {'count': len(services), 'items': services}}

  if se.caption:
    photo['tagline'] = se.caption

  if se.service_id == Service.FACEBOOK_ID:

    json_obj = load_string(se.json)

    # for some reason not all facebook photo events have an image property; if
    # it doesn't skip it
    if 'images' not in json_obj:
      log.warning('Skipping Facebook event with no images')
      return None

    # default selection to first image
    selection = json_obj['images'][0]

    # find the minimum width photo above 640
    min_resolution = sys.maxint
    for candidate in json_obj.get('images', []):
      if candidate['width'] > 640:
        selection = candidate if candidate['width'] < min_resolution else selection

    if selection and 'source' in selection:
      photo['url'] = selection['source']
      photo['width'] = selection['width']
      photo['height'] = selection['height']

  elif se.service_id == Service.INSTAGRAM_ID:

    json_obj = load_string(se.json)

    selection = json_obj['images']['standard_resolution']
    photo['url'] = selection['url']
    photo['width'] = selection['width']
    photo['height'] = selection['height']

    if 'location' in json_obj:
      photo['location'] = json_obj['location']

  return photo
