'''
Created on Dec, 2011

@author: howard
'''

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from pyramid.view import view_config

from miapi.models import DBSession

from mi_schema.models import Author, AccessGroup, AuthorAccessGroupMap, AuthorGroup, AuthorGroupMap

from miapi.globals import ACCESS_GROUP_AUTHORS, DEFAULT_AUTHOR_GROUP

from .feature_utils import getAuthorFeatures

log = logging.getLogger(__name__)


class AuthorController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()

  ##
  ## authors
  ##

  # GET /v1/authors
  #
  # get list of all authors
  @view_config(route_name='authors', request_method='GET', renderer='jsonp', http_cache=0)
  def authorsList(self):

    authorlist = []
    for author in self.dbSession.query(Author).order_by(Author.author_name):
      authorJSON = author.toJSONObject()
      authorlist.append(authorJSON)

    return {'authors': authorlist}

  # GET /v1/authors/{authorname}
  #
  # get information about a single author
  @view_config(route_name='author.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def authorGet(self):

    authorName = self.request.matchdict['authorname']

    try:
      author = self.dbSession.query(Author).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}
  
    authorJSONObj = author.toJSONObject()
    authorJSONObj['features'] = getAuthorFeatures(self.dbSession,author.id)

    return {'author': authorJSONObj}


  ##
  ## Create/update/delete author
  ##
  
  # PUT /v1/authors/{authorname}
  #
  # create a new author or update an existing author
  @view_config(route_name='author.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def authorPut(self):
  
    authorName = self.request.matchdict['authorname']
  
    authorInfo = self.request.json_body
    
    # get record for authorName.  There must be at most only 1 authorName.  No result found indicates
    # we're to perform an add; multiple results found is an internal error; 
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except NoResultFound:
      author = None
    except MultipleResultsFound:
      self.request.response.status_int = 500
      return {'error':'multiple results found for author name: %s' % authorName}

    if author:
      '''
      update
      '''
      password = authorInfo.get('password')
      if password:
        author.password = password
      
      fullname = authorInfo.get('fullname')
      if fullname:
        author.full_name = fullname
      
      email = authorInfo.get('email')
      if email:
        author.email = email
      
      template = authorInfo.get('template')
      if template:
        author.template = template

      try:
        self.dbSession.flush()
        authorJSON = author.toJSONObject()
        self.dbSession.commit()

      except Exception, e:
        self.dbSession.rollback()
        log.error(e.message)
        self.request.response.status_int = 500
        return {'error':e.message}
        
    else:
      '''
      add
      '''
      try:
      
        password = authorInfo.get('password')
        if password == None:
          self.request.response.status_int = 400
          return {'error':'Missing required property: password'}
        
        fullname = authorInfo.get('fullname')
        if fullname == None:
          self.request.response.status_int = 400
          return {'error':'Missing required property: fullname'}
        
        email = authorInfo.get('email')
        if email == None:
          self.request.response.status_int = 400
          return {'error':'Missing required property: email'}
        
        template = authorInfo.get('template')
        
        author = Author(authorName,email,fullname,password,template)
        self.dbSession.add(author)
        self.dbSession.flush() # flush so we can get the id
        
        ''' ??? this might only be temporary ???
            Create a default group (follow) and add the author to that group
            so that author is following themselves.
        '''
        
        authorGroup = AuthorGroup(author.id,DEFAULT_AUTHOR_GROUP)
        self.dbSession.add(authorGroup)
        self.dbSession.flush()
     
        mapping = AuthorGroupMap(authorGroup.id,author.id)
        self.dbSession.add(mapping)
        self.dbSession.flush()
    
        ''' Add the new author to the authors access group '''
        groupId, = self.dbSession.query(AccessGroup.id).filter_by(group_name=ACCESS_GROUP_AUTHORS).one()
        authorAccessGroupMap = AuthorAccessGroupMap(author.id,groupId)
        self.dbSession.add(authorAccessGroupMap)
        self.dbSession.flush()
    
        authorJSON = author.toJSONObject()
      
        self.dbSession.commit()
    
        log.info("create author %s and added to group %s" % (authorName, ACCESS_GROUP_AUTHORS))
    
      except IntegrityError, e:
        self.dbSession.rollback()
        log.error(e.message)
        self.request.response.status_int = 409
        return {'error':e.message}
    
      except NoResultFound, e:
        self.dbSession.rollback()
        log.error(e.message)
        self.request.response.status_int = 409
        return {'error': e.message}
  
    return {'author': authorJSON}


  # DELETE /v1/authors/{authorname}
  #
  # delete existing author
  @view_config(route_name='author.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def authorDelete(self):
  
    authorName = self.request.matchdict['authorname']
  
    author = self.dbSession.query(Author).filter(Author.author_name==authorName).first()
    if not author:
      self.request.response.status_int = 404;
      return {'error':'unknown author: %s' % authorName}  
    
    self.dbSession.delete(author)
    
    self.dbSession.commit()  
  
    log.info("deleted author: %s" % authorName)
  
    return {}
  

  ##
  ## register user
  ##
  
  # register a new instance of an app -- web, mobile app, etc.
  @view_config(route_name='author.metrics.visitor.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def authorRegisterUser(self):
  
    authorname = self.request.matchdict['authorname']
    userid = self.request.matchdict['userID']
  
    author = self.dbSession.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error':'unknown authorname'}

    return {'author':authorname,'user_id':userid,'registered':True}


  @view_config(route_name='author.metrics.visitor.CRUD', request_method='POST', renderer='jsonp', http_cache=0)
  def authorRegisterUsage(self):
  
    authorname = self.request.matchdict['authorname']
    userid = self.request.matchdict['userID']
  
    author = self.dbSession.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error':'unknown authorname'}
  
    return {'author':authorname,'user_id':userid,'registered':True}
