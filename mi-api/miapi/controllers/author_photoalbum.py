'''
Created on Jun 14, 2012

@author: howard
'''

import sys
import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from tim_commons.json_serializer import load_string

from miapi.models import DBSession

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service, AuthorServiceMap

log = logging.getLogger(__name__)


def get_album_name(event):

  well_known_albums = {AuthorServiceMap.ALL_PHOTOS_ID: 'All Photos',
                       AuthorServiceMap.OFME_PHOTOS_ID: 'Photos of Me',
                       AuthorServiceMap.LIKED_PHOTOS_ID: 'Photos I Like'}

  return well_known_albums[event.event_id[:event.event_id.index('@')]] if event.service_id == Service.ME_ID else event.caption


def make_photo_obj(event):

  photo = {'type': 'photo', 'id': event.id}

  if event.service_id == Service.FACEBOOK_ID:

    json_obj = load_string(event.json)

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

    if selection:
      photo['url'] = selection['source']
      photo['width'] = selection['width']
      photo['height'] = selection['height']

  elif event.service_id == Service.INSTAGRAM_ID:

    json_obj = load_string(event.json)

    selection = json_obj['images']['standard_resolution']
    photo['url'] = selection['url']
    photo['width'] = selection['width']
    photo['height'] = selection['height']

  return photo


class AuthorPhotoAlbumController(object):

  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()

  # GET /v1/authors/{authorname}/photoalbums
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def list_photo_albums(self):

    author_name = self.request.matchdict['authorname']

    dbSession = DBSession()

    try:
      author_id, = dbSession.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    albums = []

    # get all well know albums first
    for album in dbSession.query(ServiceEvent). \
                            filter(and_(ServiceEvent.author_id == author_id,
                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                                        ServiceEvent.service_id == Service.ME_ID)). \
                            order_by(ServiceEvent.id):

      # create the base album obj
      album_obj = {'type': 'photo-album', 'id': album.id, 'name': get_album_name(album)}

      # get the most recent photo for the cover photo
      photo = dbSession.query(ServiceEvent). \
                          filter(and_(ServiceEvent.author_id == author_id,
                                      ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                          order_by(ServiceEvent.create_time.desc()). \
                          first()

      cover_photo = make_photo_obj(photo)
      if cover_photo:
        album_obj['cover_photo'] = cover_photo

      albums.append(album_obj)

    # get all other albums
    for album in dbSession.query(ServiceEvent). \
                            filter(and_(ServiceEvent.author_id == author_id,
                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                                        ServiceEvent.service_id != Service.ME_ID)). \
                            order_by(ServiceEvent.create_time.desc()):

      cover_photo = None

      if album.service_id == Service.FACEBOOK_ID:
        # get the cover photo
        json_obj = load_string(album.json)
        photo_id = json_obj.get('cover_photo')
        if photo_id:
          try:
            photo = dbSession.query(ServiceEvent). \
                                filter(and_(ServiceEvent.service_id == Service.FACEBOOK_ID,
                                            ServiceEvent.event_id == photo_id)).one()
            cover_photo = make_photo_obj(photo)
          except NoResultFound:
            pass

      album_obj = {'type': 'photo-album', 'id': album.id, 'name': get_album_name(album)}
      if cover_photo:
        album_obj['cover_photo'] = cover_photo

      albums.append(album_obj)

    return {'author_name': author_name, 'photo_albums': albums}