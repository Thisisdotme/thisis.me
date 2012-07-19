from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_
from pyramid.view import view_config

from tim_commons import db
from mi_schema.models import Author, ServiceObjectType, ServiceEvent, AuthorServiceMap
from author_utils import createServiceEvent
from . import get_tim_author_fragment

import data_access.service


class AuthorPhotoAlbumController(object):

  def __init__(self, request):
    self.request = request
    self.db_session = db.Session()

  # GET /v1/authors/{authorname}/photoalbums
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def list_photo_albums(self):

    author_name = self.request.matchdict['authorname']

    try:
      author_id = self.db_session.query(Author.id).filter_by(author_name=author_name).scalar()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    albums = []

    # get all well know albums first
    for album, asm, author in self.db_session. \
      query(ServiceEvent, AuthorServiceMap, Author). \
      join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                  ServiceEvent.service_id == AuthorServiceMap.service_id)). \
      join(Author, ServiceEvent.author_id == Author.id). \
      filter(and_(ServiceEvent.author_id == author_id,
                  ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                  ServiceEvent.service_id == data_access.service.name_to_id('me'))). \
      order_by(ServiceEvent.id):

      album_obj = createServiceEvent(self.db_session, self.request, album, asm, author)
      if album_obj['post_type_detail']['photo_album']['photo_count'] > 0:
        albums.append(album_obj)

    # get all other albums
    for album, asm, author in self.db_session. \
      query(ServiceEvent, AuthorServiceMap, Author). \
      join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                  ServiceEvent.service_id == AuthorServiceMap.service_id)). \
      join(Author, ServiceEvent.author_id == Author.id). \
      filter(and_(ServiceEvent.author_id == author_id,
                  ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE,
                  ServiceEvent.service_id != data_access.service.name_to_id('me'))). \
      order_by(ServiceEvent.create_time.desc()):

      album_obj = createServiceEvent(self.db_session, self.request, album, asm, author)
      if album_obj['post_type_detail']['photo_album']['photo_count'] > 0:
        albums.append(album_obj)

    # if only 2 albums exist and they contain the same number of photos remove the
    # first (which is the 'all photos' album)
    if len(albums) == 2 and (albums[0]['post_type_detail']['photo_album']['photo_count'] == albums[1]['post_type_detail']['photo_album']['photo_count']):
      albums.pop(0)

    return {'author': get_tim_author_fragment(self.request, author_name),
            'photo_albums': albums,
            'paging': {'prev': None, 'next': None}}
