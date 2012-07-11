from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config
from tim_commons import db
from mi_schema.models import (
    Author,
    ServiceObjectType,
    ServiceEvent,
    Service,
    Relationship,
    AuthorServiceMap)
import data_access.service

from . import make_photo_obj, get_album_name


class AuthorPhotoController(object):

  def __init__(self, request):
    self.request = request
    self.db_session = db.Session()

  # GET /v1/authors/{authorname}/photoalbums/{albumname}/photos
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.photos.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def get_photos(self):

    author_name = self.request.matchdict['authorname']
    album_id = self.request.matchdict['albumID']

    try:
      author_id, = self.db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      album = self.db_session.query(ServiceEvent).filter_by(id=album_id, type_id=ServiceObjectType.PHOTO_ALBUM_TYPE).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown album %s' % album_id}

    photos = []
    if album.service_id == data_access.service.name_to_id('me'):
      # handle photos for well-known albums
      for event, asm, author in self.db_session. \
          query(ServiceEvent, AuthorServiceMap, Author). \
          join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                      ServiceEvent.service_id == AuthorServiceMap.service_id)). \
          join(Author, ServiceEvent.author_id == Author.id). \
          filter(and_(ServiceEvent.author_id == author_id,
                      ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
          order_by(ServiceEvent.create_time.desc()). \
          limit(200):
        photo = make_photo_obj(self.db_session, self.request, event, asm, author)
        if photo:
          photos.append(photo)
    else:
      # handle photos for other albums
      for event, asm, author in self.db_session. \
          query(ServiceEvent, AuthorServiceMap, Author). \
          join(Relationship, and_(Relationship.child_author_id == ServiceEvent.author_id,
                                  Relationship.child_service_id == ServiceEvent.service_id,
                                  Relationship.child_service_event_id == ServiceEvent.event_id)). \
          join(AuthorServiceMap, and_(ServiceEvent.author_id == AuthorServiceMap.author_id,
                                      ServiceEvent.service_id == AuthorServiceMap.service_id)). \
          join(Author, ServiceEvent.author_id == Author.id). \
          filter(and_(Relationship.parent_author_id == author_id,
                      Relationship.parent_service_id == album.service_id,
                      Relationship.parent_service_event_id == album.event_id)). \
          order_by(ServiceEvent.create_time.desc()):
        photo = make_photo_obj(self.db_session, self.request, event, asm, author)
        if photo:
          photos.append(photo)

    return {'type': 'photo-album',
            'id': album.id,
            'headline': get_album_name(album),
            'photos': photos}
