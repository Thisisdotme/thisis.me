import logging
import calendar

from sqlalchemy import func, and_
from sqlalchemy.orm.exc import NoResultFound

from tim_commons.json_serializer import load_string
from tim_commons import db

from data_access import service, post_type

from mi_schema.models import (
    Author,
    AuthorServiceMap,
    Service,
    ServiceObjectType,
    ServiceEvent,
    Relationship)

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


def get_tim_author_fragment(request, author_name):

  author, asm = db.Session().query(Author, AuthorServiceMap). \
                             join(AuthorServiceMap, Author.id == AuthorServiceMap.author_id). \
                             filter(Author.author_name == author_name). \
                             filter(AuthorServiceMap.service_id == service.name_to_id('me')).one()

  # for sure properties
  author_obj = {'service_name': 'me',
                'id': author.id,
                'name': author.author_name,
                'full_nane': author.full_name}

  author_obj['picture'] = get_profile_image_fragment(request, asm)

  return author_obj


def get_service_author_fragment(request, asm, author):

  profile_image_url = asm.profile_image_url
  if profile_image_url is None:
    profile_image_url = request.static_url('miapi:%s' % 'img/profile_placeholder.png')

  author_obj = {'service_name': service.id_to_service[asm.service_id].service_name,
                'id': asm.service_author_id,
                'name': author.author_name,     # TODO these need to become service user-name
                'full_name': author.full_name}  # TODO and service full-name

  author_obj['picture'] = get_profile_image_fragment(request, asm)

  return author_obj


def get_known_event_info_fragment(request, se, asm, author):

  event_info = {'service_name': service.id_to_service[se.service_id].service_name,
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
  if se.service_id == service.name_to_id('instagram') and se.json:
    json_obj = load_string(se.json)
    if 'location' in json_obj:
      # TODO this needs to be normalized to thisis.me's structure using the event interpreter
      location_info = json_obj['location']

  return location_info


def get_album_name(event):

  well_known_albums = {ServiceEvent.ALL_PHOTOS_ID: 'All Photos',
                       ServiceEvent.OFME_PHOTOS_ID: 'Photos of Me',
                       ServiceEvent.LIKED_PHOTOS_ID: 'Photos I Like'}

  if event.service_id == service.name_to_id('me'):
    return well_known_albums[event.event_id[:event.event_id.index('@')]]
  else:
    return event.caption


def _get_album_count(db_session, se):
  # check for the special well-known album "all photos"
  if se.event_id == ServiceEvent.make_well_known_service_event_id(ServiceEvent.ALL_PHOTOS_ID, se.author_id):
    count = db_session.query(func.count(ServiceEvent.id)). \
                       filter(and_(ServiceEvent.author_id == se.author_id,
                                   ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                       scalar()
  else:
    count = db_session.query(func.count(Relationship.child_service_event_id)). \
                       filter(and_(Relationship.parent_author_id == se.author_id,
                                   Relationship.parent_service_id == se.service_id, \
                                   Relationship.parent_service_event_id == se.event_id)). \
                       scalar()
  return count


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

  facebook_service_id = service.name_to_id('facebook')

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
      cover_photos = _get_top_album_photos(db_session, album_se, author)

  else:
    cover_photos = _get_top_album_photos(db_session, album_se, author)

  return {'photo_count': _get_album_count(db_session, album_se),
          'cover_photos': cover_photos}


def _get_top_album_photos(db_session, album_se, author):

  photos = []

  # check if this is the ALL well-known album
  if ServiceEvent.make_well_known_service_event_id(ServiceEvent.ALL_PHOTOS_ID, author.id) == album_se.event_id:
    for photo_se in db_session.query(ServiceEvent). \
          filter(and_(ServiceEvent.author_id == author.id,
                      ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(PHOTO_ALBUM_COVER_LIMIT):
      photo = get_photo_detail_fragment(photo_se)
      if photo:
        photos.append(photo)
  else:
    for photo_se in db_session.query(ServiceEvent). \
          join(Relationship, and_(Relationship.child_author_id == ServiceEvent.author_id,
                                  Relationship.child_service_id == ServiceEvent.service_id,
                                  Relationship.child_service_event_id == ServiceEvent.event_id)). \
          filter(and_(Relationship.parent_author_id == album_se.author_id,
                      Relationship.parent_service_id == album_se.service_id,
                      Relationship.parent_service_event_id == album_se.event_id)). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(PHOTO_ALBUM_COVER_LIMIT):

      photo = get_photo_detail_fragment(photo_se)
      if photo:
          photos.append(photo)

  return photos if len(photos) > 0 else None


def get_photo_detail_fragment(se):

    size_ordered_images = {}
    if se.service_id == service.name_to_id('facebook'):

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

    elif se.service_id == service.name_to_id('instagram'):

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
