'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from miapi.models import DBSession
from mi_schema.models import Author

log = logging.getLogger(__name__)


# return all authors that match the specified search criteria
#
@view_config(route_name='search.author', request_method='GET', renderer='jsonp', http_cache=0)
def searchAuthors(request):

  dbSession = DBSession()

  # get author-id for authorName
  try:
    authorList = []
    searchTerm = request.GET.get('name')
    if not searchTerm:
      request.response.status_int = 400;
      return {'error':'missing required query arg: name'}
      
    likeExpr = '%' + searchTerm + '%' 
    for authorName, in dbSession.query(Author.author_name).filter(Author.author_name.like(likeExpr)).order_by(Author.author_name):
      authorList.append(authorName) 
  except:
    request.response.status_int = 404;
    return {'error':'unknown error'}
  
  return authorList;

