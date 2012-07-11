import logging
import calendar

from sqlalchemy import func, and_

from tim_commons.json_serializer import load_string
import data_access.service

from mi_schema.models import (
    ServiceObjectType,
    ServiceEvent,
    Relationship)

from miapi import service_object_type_dict


def get_author_info(request, asm, author):

  profile_image_url = asm.profile_image_url
  if profile_image_url is None:
    profile_image_url = request.static_url('miapi:%s' % 'img/profile_placeholder.png')

  author_obj = {'profile_image_url': profile_image_url,
                'name': author.author_name,
                'full_name': author.full_name}

  return author_obj


def get_album_name(event):

  well_known_albums = {ServiceEvent.ALL_PHOTOS_ID: 'All Photos',
                       ServiceEvent.OFME_PHOTOS_ID: 'Photos of Me',
                       ServiceEvent.LIKED_PHOTOS_ID: 'Photos I Like'}

  if event.service_id == data_access.service.name_to_id('me'):
    return well_known_albums[event.event_id[:event.event_id.index('@')]]
  else:
    return event.caption


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


def make_photo_obj(db_session, request, se, asm, author):
  link = request.route_url('author.query.events.eventId',
                           authorname=author.author_name,
                           eventID=se.id)

  if data_access.service.name_to_id('me') == se.service_id:
    # we just want to return the json after adding the links to it
    event = load_string(se.json)
    event['link'] = link
    event['id'] = se.id
    event['event_id'] = se.id
    for source in event['sources']['items']:
      link = 'miapi:img/l/services/color/{0}.png'.format(source['service_name'])
      source['link'] = request.static_url(link)

    return event
  else:
    photo = {'type': service_object_type_dict[ServiceObjectType.PHOTO_TYPE],
             'id': se.id,
             'create_time': calendar.timegm(se.create_time.timetuple()),
             'author': get_author_info(request, asm, author),
             'link': link,
             'service': data_access.service.id_to_service[se.service_id].service_name,
             'sources': {'count': 0, 'items': []}}

    if se.caption:
      photo['label'] = se.caption

    size_ordered_images = {}
    if se.service_id == data_access.service.name_to_id('facebook'):
      json_obj = load_string(se.json)

      # for some reason not all facebook photo events have an image property; if
      # it doesn't skip it
      if 'images' not in json_obj:
        logging.warning('Skipping Facebook event with no images')
        return None

      for candidate in json_obj.get('images', []):

        size = candidate.get('width', 0) * candidate.get('height', 0)

        image = {'url': candidate['source'],
                 'width': candidate['width'],
                 'height': candidate['height']}

        size_ordered_images[size] = image

    elif se.service_id == data_access.service.name_to_id('instagram'):

      json_obj = load_string(se.json)

      for candidate in json_obj['images'].itervalues():

        size = candidate.get('width', 0) * candidate.get('height', 0)

        image = {'url': candidate['url'],
                 'width': candidate['width'],
                 'height': candidate['height']}

        size_ordered_images[size] = image

      if 'location' in json_obj:
        photo['location'] = json_obj['location']

    images = []
    for size, image in sorted(size_ordered_images.iteritems(), key=lambda x: x[1]):
      images.append(image)

    photo['images'] = images

    return photo
