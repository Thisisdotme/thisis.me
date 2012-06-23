'''
Created on Jun 14, 2012

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from tim_commons.json_serializer import load_string

from miapi.models import DBSession

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service, AuthorServiceMap

from . import make_photo_obj, make_photo_album_obj

log = logging.getLogger(__name__)


class AuthorPhotoAlbumController(object):

  def __init__(self, request):
    self.request = request
    self.db_session = DBSession()

  # GET /v1/authors/{authorname}/photoalbums
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def list_photo_albums(self):

    author_name = self.request.matchdict['authorname']

    db_session = DBSession()

    try:
      author_id, = db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    albums = []

    # get all well know albums first
    for album, asm, author, service_name in self.db_session. \
                                 query(ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
                                 join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                                             ServiceEvent.service_id == AuthorServiceMap.service_id)). \
                                 join(Author, ServiceEvent.author_id == Author.id). \
                                 join(Service, ServiceEvent.service_id == Service.id). \
                                 filter(and_(ServiceEvent.author_id == author_id,
                                             ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                                             ServiceEvent.service_id == Service.ME_ID)). \
                                 order_by(ServiceEvent.id):

      # create the base album obj
      album_obj = make_photo_album_obj(self.db_session, self.request, album, asm, author, service_name)
      if album_obj:

        # get the most recent photo for the cover photo
        photo, asm, author, service_name = self.db_session.query(ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
                                         join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                                                     ServiceEvent.service_id == AuthorServiceMap.service_id)). \
                                         join(Author, ServiceEvent.author_id == Author.id). \
                                         join(Service, ServiceEvent.service_id == Service.id). \
                                         filter(and_(ServiceEvent.author_id == author_id,
                                                     ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                                         order_by(ServiceEvent.create_time.desc()). \
                                         first()

        cover_photo = make_photo_obj(self.db_session, self.request, photo, asm, author, service_name)
        if cover_photo:
          album_obj['cover_photo'] = cover_photo

        albums.append(album_obj)

    # get all other albums
    for album, asm, author, service_name in self.db_session. \
                            query(ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
                            join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                                        ServiceEvent.service_id == AuthorServiceMap.service_id)). \
                            join(Author, ServiceEvent.author_id == Author.id). \
                            join(Service, ServiceEvent.service_id == Service.id). \
                            filter(and_(ServiceEvent.author_id == author_id,
                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                                        ServiceEvent.service_id != Service.ME_ID)). \
                            order_by(ServiceEvent.create_time.desc()):

      album_obj = make_photo_album_obj(self.db_session, self.request, album, asm, author, service_name)
      if album_obj:
        cover_photo = None

        if album.service_id == Service.FACEBOOK_ID:
          # get the cover photo
          json_obj = load_string(album.json)
          photo_id = json_obj.get('cover_photo')
          if photo_id:
            try:
              photo, asm, author, service_name = db_session. \
                                        query(ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
                                        join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                                                    ServiceEvent.service_id == AuthorServiceMap.service_id)). \
                                        join(Author, ServiceEvent.author_id == Author.id). \
                                        join(Service, ServiceEvent.service_id == Service.id). \
                                        filter(and_(ServiceEvent.service_id == Service.FACEBOOK_ID,
                                                    ServiceEvent.event_id == photo_id)).one()
              cover_photo = make_photo_obj(self.db_session, self.request, photo, asm, author, service_name)
            except NoResultFound:
              pass

        if cover_photo:
          album_obj['cover_photo'] = cover_photo

        albums.append(album_obj)

    db_session.commit()

    return {'author_name': author_name, 'photo_albums': albums}