'''
Created on Jun 14, 2012

@author: howard
'''

import logging
import sys

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from pyramid.view import view_config

from miapi.models import DBSession

from tim_commons.json_serializer import load_string

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service


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
    album_name = self.request.matchdict['albumname']

    dbSession = DBSession()

    try:
      author_id, = dbSession.query(Author.id).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    photos = []
    for event in dbSession.query(ServiceEvent). \
                            filter(and_(ServiceEvent.author_id == author_id,
                                        ServiceEvent.type_id == ServiceObjectType.PHOTO_TYPE)). \
                            order_by(ServiceEvent.create_time.desc()). \
                            limit(200):

      photo = {'type': 'photo', 'id': event.id}

      if event.service_id == Service.FACEBOOK_ID:

        json_obj = load_string(event.json)

        # for some reason not all facebook photo events have an image property; if
        # it doesn't skip it
        if 'images' not in json_obj:
          continue

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

      photos.append(photo)

    return {'author_name': author_name, 'photo_album': album_name, 'photos': photos}