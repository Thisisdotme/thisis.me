'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from tim_commons import db

from mi_schema.models import Author

log = logging.getLogger(__name__)


class AuthorSearchController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request
      self.db_session = db.Session()

  # return all authors that match the specified search criteria
  #
  @view_config(route_name='search.author', request_method='GET', renderer='jsonp', http_cache=0)
  def searchAuthors(self):

    # get author-id for authorName
    try:
      authorList = []
      searchTerm = self.request.GET.get('name')
      if not searchTerm:
        self.request.response.status_int = 400
        return {'error': 'missing required query arg: name'}

      likeExpr = '%' + searchTerm + '%'
      for authorName, in self.db_session.query(Author.author_name).filter(Author.author_name.like(likeExpr)).order_by(Author.author_name):
        authorList.append(authorName)
    except:
      self.equest.response.status_int = 404
      return {'error': 'unknown error'}

    return authorList
