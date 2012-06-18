'''
Created on Jun 14, 2012

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, ServiceObjectType, ServiceEvent


log = logging.getLogger(__name__)


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

    albums = [{'type': 'photo-album', 'name': 'All Photos'},
              {'type': 'photo-album', 'name': 'Photos of Me'},
              {'type': 'photo-album', 'name': 'Photos I Like'}]
    for album in dbSession.query(ServiceEvent). \
                            filter(and_(ServiceEvent.author_id == author_id,
                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE)). \
                            order_by(ServiceEvent.create_time.desc()):
      albums.append({'type': 'photo-album', 'id': album.id, 'name': album.caption})

    return {'author_name': author_name, 'photo_albums': albums}