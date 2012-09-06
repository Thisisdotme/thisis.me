import logging
import calendar
import datetime

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from tim_commons.json_serializer import load_string

import data_access.service
import data_access.service_event

from mi_schema.models import (
    ServiceObjectType,
    ServiceEvent)

PHOTO_ALBUM_COVER_LIMIT = 3


def get_profile_image_fragment(request, asm):
  # include actual profile image or place-holder depending on existence
  if asm.profile_image_url:
    picture_obj = {'image_url': asm.profile_image_url}
# TODO add width and height to author_service_map
#    if asm.profile_image_width > 0:
#      picture_obj['width'] = asm.profile_image_width
#    if asm.profile_image_height > 0:
#      picture_obj['height'] = asm.profile_image_height
  else:
    picture_obj = {'image_url': request.static_url('miapi:%s' % 'img/profile_placeholder.png')}
# TODO determine width and height for profile image placeholder
#    if asm.profile_image_width > 0:
#      picture_obj['width'] = 16
#    if asm.profile_image_height > 0:
#      picture_obj['height'] = 16

  return picture_obj


def get_service_author_fragment(request, asm, author):

  profile_image_url = asm.profile_image_url
  if profile_image_url is None:
    profile_image_url = request.static_url('miapi:%s' % 'img/profile_placeholder.png')

  author_obj = {'service_name': data_access.service.id_to_name(asm.service_id),
                'id': asm.service_author_id,
                'name': author.author_name,     # TODO these need to become service user-name
                'full_name': author.full_name}  # TODO and service full-name

  author_obj['picture'] = get_profile_image_fragment(request, asm)

  return author_obj


def get_known_event_info_fragment(request, se, asm, author):

  event_info = {'service_name': data_access.service.id_to_name(se.service_id),
                'service_event_id': se.event_id,
                'service_user': get_service_author_fragment(request, asm, author)
                }

  if se.url:
    event_info['service_url'] = se.url

  # TODO add num_comments and num_likes properties

  return event_info


def get_unknown_event_info_fragment(se):

  event_info = {'domain': '',
                'small_icon': '',
                'url': ''}

  return event_info

  pass


def get_location_fragment(se):

  location_info = None
  if se.service_id == data_access.service.name_to_id('instagram') and se.json:
    json_obj = load_string(se.json)
    if 'location' in json_obj:
      # TODO this needs to be normalized to thisis.me's structure using the event interpreter
      location_info = json_obj['location']

  return location_info


def get_album_name(event):

  well_known_albums = {ServiceEvent.ALL_PHOTOS_ID: 'All Photos',
                       ServiceEvent.OFME_PHOTOS_ID: 'Photos of Me',
                       ServiceEvent.LIKED_PHOTOS_ID: 'Photos I Like'}

  if event.service_id == data_access.service.name_to_id('me'):
    return well_known_albums[event.event_id[:event.event_id.index('@')]]
  else:
    return event.caption


def _get_album_count(db_session, se):
  return data_access.service_event.compute_album_count(se.author_id, se.service_id, se.event_id)


def get_post_type_detail_fragment(db_session, se, author):

  post_type_info = None

  if se.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE:
    post_type_info = get_photo_album_detail_fragment(db_session, se, author)
  elif se.type_id == ServiceObjectType.PHOTO_TYPE:
    post_type_info = get_photo_detail_fragment(se)
  elif se.type_id == ServiceObjectType.CHECKIN_TYPE:
    pass
  elif se.type_id == ServiceObjectType.STATUS_TYPE:
    pass
  elif se.type_id == ServiceObjectType.VIDEO_ALBUM_TYPE:
    pass
  elif se.type_id == ServiceObjectType.VIDEO_TYPE:
    pass
  elif se.type_id == ServiceObjectType.FOLLOW_TYPE:
    pass
  elif se.type_id == ServiceObjectType.CORRELATION_TYPE:
    pass
  elif se.type_id == ServiceObjectType.HIGHLIGHT_TYPE:
    pass

  return post_type_info


def get_photo_album_detail_fragment(db_session, album_se, author):
  # select the first 3 photos in the album for the cover art
  # TODO complete

  cover_photos = []

  facebook_service_id = data_access.service.name_to_id('facebook')

  if album_se.service_id == facebook_service_id:

    json_obj = load_string(album_se.json)

    # get the cover photo if it exists otherwise get top photos
    photo_id = json_obj.get('cover_photo')
    if photo_id:
      try:
        photo_se = db_session.query(ServiceEvent). \
            filter(and_(ServiceEvent.service_id == facebook_service_id,
                        ServiceEvent.event_id == photo_id)). \
            one()
        photo = get_photo_detail_fragment(photo_se)
        if photo:
          cover_photos.append(photo)

      except NoResultFound:
        pass
    else:
      cover_photos = _get_top_album_photos(db_session, album_se)

  else:
    cover_photos = _get_top_album_photos(db_session, album_se)

  return {'photo_count': _get_album_count(db_session, album_se),
          'cover_photos': cover_photos}


def _get_top_album_photos(db_session, album_se):

  photos = []

  photo_rows = data_access.service_event.query_photos_page(
      album_se.author_id,
      album_se.event_id,
      album_se.service_id,
      PHOTO_ALBUM_COVER_LIMIT)

  for photo_se in photo_rows:
    photo = get_photo_detail_fragment(photo_se)
    if photo:
      photos.append(photo)

  return photos if len(photos) > 0 else None


def get_photo_detail_fragment(se):

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

        image = {'image_url': candidate['source'],
                 'width': candidate['width'],
                 'height': candidate['height']}

        size_ordered_images[size] = image

    elif se.service_id == data_access.service.name_to_id('instagram'):

      json_obj = load_string(se.json)

      for candidate in json_obj['images'].itervalues():

        size = candidate.get('width', 0) * candidate.get('height', 0)

        image = {'image_url': candidate['url'],
                 'width': candidate['width'],
                 'height': candidate['height']}

        size_ordered_images[size] = image

    images = []
    for size, image in sorted(size_ordered_images.iteritems(), key=lambda x: x[1]):
      images.append(image)

    return images


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
