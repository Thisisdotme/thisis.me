'''
Created on Jun 14, 2012

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service, Relationship

from author_photoalbum import get_album_name

from . import make_photo_obj

log = logging.getLogger(__name__)


class AuthorPhotoController(object):

  def __init__(self, request):
    self.request = request
    self.db_session = DBSession()

  # GET /v1/authors/{authorname}/photoalbums/{albumname}/photos
  #
  # list all services associated with the author
  @view_config(route_name='author.photoalbums.photos.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def list_photo_albums(self):

    author_name = self.request.matchdict['authorname']
    album_id = self.request.matchdict['albumID']

    db_session = DBSession()

    try:
      author_id, = db_session.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    try:
      album = db_session.query(ServiceEvent).filter_by(id=album_id, type_id=ServiceObjectType.PHOTO_ALBUM_TYPE).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown album %s' % album_id}

    photos = []
    if album.service_id == Service.ME_ID:
      # handle photos for well-known albums
      for event, service_name in db_session.query(ServiceEvent, Service.service_name). \
                                            join(Service, ServiceEvent.service_id == Service.id). \
                                            filter(and_(ServiceEvent.author_id == author_id,
                                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                                            order_by(ServiceEvent.create_time.desc()). \
                                            limit(200):
        photo = make_photo_obj(self.db_session, self.request, event, service_name)
        if photo:
          photos.append(photo)
    else:
      # handle photos for other albums
      for event, service_name in db_session.query(ServiceEvent, Service.service_name). \
                                            join(Relationship, and_(Relationship.child_author_id == ServiceEvent.author_id,
                                                                    Relationship.child_service_id == ServiceEvent.service_id,
                                                                    Relationship.child_service_event_id == ServiceEvent.event_id)). \
                                            join(Service, ServiceEvent.service_id == Service.id). \
                                            filter(and_(Relationship.parent_author_id == author_id,
                                                        Relationship.parent_service_id == album.service_id,
                                                        Relationship.parent_service_event_id == album.event_id)). \
                                            order_by(ServiceEvent.create_time.desc()):
        photo = make_photo_obj(self.db_session, self.request, event, service_name)
        if photo:
          photos.append(photo)

    return {'type': 'photo-album', 'id': album.id, 'name': get_album_name(album), 'photos': photos}