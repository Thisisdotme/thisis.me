'''
Created on Apr 16, 2012

@author: howard
'''
import os
import logging
import mimetypes

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import Author

from timmobilev2.models import DBSession

log = logging.getLogger(__name__)


class OverrideController(object):

  def __init__(self, request):
    self.request = request
    self.db_session = DBSession()

  @view_config(route_name='resource.any', request_method='GET', http_cache=0)
  def OverrideResourceHandler(self):

    log.debug("ANY override handler")

    author_name = self.request.matchdict['authorname']
    resource = self.request.matchdict['resource']
    ext = self.request.matchdict['ext']

    base = os.path.dirname(os.path.dirname(__file__))

    # check for a custom asset
    candidate = '%s/assets/custom/%s/%s.%s' % (base, author_name, resource, ext)
    if os.path.exists(candidate):
      asset = open(candidate)
      contentType = mimetypes.guess_type(candidate)[0]
      return Response(content_type=contentType, app_iter=asset)
    else:
      # check for a stock asset based on the author's configured template
      try:
        template, = self.db_session.query(Author.template).filter_by(author_name=author_name).one()
        self.db_session.commit()
        log.debug("*************GOT TEMPLATE**************")
        log.debug(template)
      except NoResultFound:
        self.db_session.rollback()
        return HTTPNotFound(self.request.path)
      candidate = '%s/assets/stock/%s/%s.%s' % (base, template, resource, ext) if template else None
      log.debug(candidate)
      if candidate and os.path.exists(candidate):
        log.debug("************* FOUND STOCK FILE!!!!!**************")
        asset = open(candidate)
        contentType = mimetypes.guess_type(candidate)[0]
        return Response(content_type=contentType, app_iter=asset)
      else:
        # check for a default asset
        candidate = '%s/assets/default/%s.%s' % (base, resource, ext)
        if os.path.exists(candidate):
          asset = open(candidate)
          contentType = mimetypes.guess_type(candidate)[0]
          return Response(content_type=contentType, app_iter=asset)
        else:
          return HTTPNotFound(self.request.path)
