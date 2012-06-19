'''
Created on Jun 14, 2012

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service

from author_photoalbum import get_album_name, make_photo_obj

log = logging.getLogger(__name__)


class AuthorPhotoController(object):

  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()

  # GET /v1/authors/{authorname}/photoalbums/{albumname}/photos
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.photos.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def list_photo_albums(self):

    author_name = self.request.matchdict['authorname']
    album_id = self.request.matchdict['albumID']

    dbSession = DBSession()

    try:
      author_id, = dbSession.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      album = dbSession.query(ServiceEvent).filter_by(id=album_id).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown album %s' % album_id}

    photos = []
    if album.service_id == Service.ME_ID:
      # handle photos for well-known albums
      for event in dbSession.query(ServiceEvent). \
                              filter(and_(ServiceEvent.author_id == author_id,
                                          ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                              order_by(ServiceEvent.create_time.desc()). \
                              limit(200):
        photo = make_photo_obj(event)
        if photo:
          photos.append(photo)
    else:
      # handle photos for other albums
      for event in dbSession.query(ServiceEvent). \
                              filter(and_(ServiceEvent.author_id == author_id,
                                          ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                              order_by(ServiceEvent.create_time.desc()). \
                              limit(200):
        photo = make_photo_obj(event)
        if photo:
          photos.append(photo)

    return {'type': 'photo-album', 'id': album.id, 'name': get_album_name(album), 'photos': photos}