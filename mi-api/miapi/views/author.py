'''
Created on Dec, 2011

@author: howard
'''

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import (Author, AccessGroup, AuthorAccessGroupMap)


log = logging.getLogger(__name__)

GROUP_AUTHORS = 'group:authors'


##
## authors
##

# get list of all authors
@view_config(route_name='authors', request_method='GET', renderer='jsonp', http_cache=0)
def authorList(request):
  
  dbsession = DBSession()
  authorlist = []
  for author in dbsession.query(Author).order_by(Author.author_name):
    authorJSON = author.toJSONObject()
    authorlist.append(authorJSON)
  
  return {'authors':authorlist}


# get information about a single author
@view_config(route_name='author.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
def authorGet(request):

  authorName = request.matchdict['authorname']

  dbsession = DBSession()
  
  try:
    author = dbsession.query(Author).filter_by(author_name=authorName).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error':'unknown author %s' % authorName}

  return {'author': author.toJSONObject()}


##
## Create/update/delete author
##

# create a new author or update an existing author
@view_config(route_name='author.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def authorPut(request):
  
  authorname = request.matchdict['authorname']
  
  password = request.params.get('password')
  if password == None:
    request.response.status_int = 400
    return {'error':'Missing required form field: password'}
  password = password
  
  fullname = request.params.get('fullname')
  if fullname == None:
    request.response.status_int = 400
    return {'error':'Missing required form field: fullname'}
  fullname = fullname
  
  email = request.params.get('email')
  if email == None:
    request.response.status_int = 400
    return {'error':'Missing required form field: email'}
  email = email
  
  dbsession = DBSession()

  author = Author(authorname,email,fullname,password)

  try:
  
    dbsession.add(author)
    dbsession.flush() # flush so we can get the id

    authorJSON = author.toJSONObject()
  
    groupId, = dbsession.query(AccessGroup.id).filter_by(group_name=GROUP_AUTHORS).one()

    authorAccessGroupMap = AuthorAccessGroupMap(author.id,groupId)

    dbsession.add(authorAccessGroupMap)

    dbsession.commit()

    log.info("create author %s and added to group %s" % (authorname, GROUP_AUTHORS))

  except IntegrityError, e:
    dbsession.rollback()
    log.error(e.message)
    request.response.status_int = 409
    return {'error':e.message}

  except NoResultFound, e:
    dbsession.rollback()
    log.error(e.message)
    request.response.status_int = 409
    return {'error': e.message}

  return {'author': authorJSON}


# delete existing author
@view_config(route_name='author.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
def authorDelete(request):

  authorName = request.matchdict['authorname']

  dbsession = DBSession()

  author = dbsession.query(Author).filter(Author.author_name==authorName).first()
  if not author:
    request.response.status_int = 404;
    return {'error':'unknown author: %s' % authorName}  
  
  dbsession.delete(author)
  
  dbsession.commit()  

  log.info("deleted author: %s" % authorName)

  return {}


##
## register user
##

# register a new instance of an app -- web, mobile app, etc.
@view_config(route_name='author.metrics.visitor.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
def authorRegisterUser(request):

  authorname = request.matchdict['authorname']
  userid = request.matchdict['userID']

  dbsession = DBSession()
  author = dbsession.query(Author).filter_by(author_name=authorname).first()
  if author == None:
    request.response.status_int = 404
    return {'error':'unknown authorname'}

  return {'author':authorname,'user_id':userid,'registered':True}


@view_config(route_name='author.metrics.visitor.CRUD', request_method='POST', renderer='jsonp', http_cache=0)
def authorRegisterUsage(request):

  authorname = request.matchdict['authorname']
  userid = request.matchdict['userID']

  dbsession = DBSession()
  author = dbsession.query(Author).filter_by(author_name=authorname).first()
  if author == None:
    request.response.status_int = 404
    return {'error':'unknown authorname'}

  return {'author':authorname,'user_id':userid,'registered':True}
