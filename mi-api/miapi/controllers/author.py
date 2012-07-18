import logging
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pyramid.view import view_config

from tim_commons import db
from mi_schema.models import (
    Author,
    AuthorReservation,
    AccessGroup,
    AuthorAccessGroupMap,
    AuthorGroup,
    AuthorGroupMap,
    AuthorServiceMap,
    ServiceObjectType,
    ServiceEvent)
import data_access.service

from miapi.globals import ACCESS_GROUP_AUTHORS, DEFAULT_AUTHOR_GROUP

from .feature_utils import getAuthorFeatures


class AuthorController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.db_session = db.Session()

  ##
  ## authors
  ##

  # GET /v1/authors
  #
  # get list of all authors
  @view_config(route_name='authors', request_method='GET', renderer='jsonp', http_cache=0)
  def authorsList(self):

    authorlist = []
    for author in self.db_session.query(Author).order_by(Author.author_name):
      authorJSON = author.toJSONObject()
      authorlist.append(authorJSON)

    return {'authors': authorlist}

  # GET /v1/authors/{authorname}
  #
  # get information about a single author
  @view_config(route_name='author.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def authorGet(self):

    author_name = self.request.matchdict['authorname']

    try:
      author = self.db_session.query(Author).filter_by(author_name=author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    authorJSONObj = author.toJSONObject()
    authorJSONObj['features'] = getAuthorFeatures(self.db_session, author.id)

    return {'author': authorJSONObj}

  ##
  ## Create/update/delete author
  ##
  # PUT /v1/authors/{authorname}
  #
  # create a new author or update an existing author
  @view_config(route_name='author.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def authorPut(self):

    author_name = self.request.matchdict['authorname']

    authorInfo = self.request.json_body

    # get record for author_name.  There must be at most only 1 author_name.  No result found indicates
    # we're to perform an add; multiple results found is an internal error;
    try:
      author = self.db_session.query(Author).filter(Author.author_name == author_name).one()
    except NoResultFound:
      author = None
    except MultipleResultsFound:
      self.request.response.status_int = 500
      return {'error': 'multiple results found for author name: %s' % author_name}

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

        self.db_session.flush()

        authorJSON = author.toJSONObject()

      except Exception, e:
        logging.error(e.message)
        self.request.response.status_int = 500
        return {'error': e.message}

    else:
      '''
      add
      '''
      try:

        password = authorInfo.get('password')
        if password == None:
          self.request.response.status_int = 400
          return {'error': 'Missing required property: password'}

        fullname = authorInfo.get('fullname')
        if fullname == None:
          self.request.response.status_int = 400
          return {'error': 'Missing required property: fullname'}

        email = authorInfo.get('email')
        if email == None:
          self.request.response.status_int = 400
          return {'error': 'Missing required property: email'}

        template = authorInfo.get('template')

        # create and insert new author
        author = Author(author_name, email, fullname, password, template)
        self.db_session.add(author)
        self.db_session.flush()

        # create and insert new author reservation
        reservation = AuthorReservation(author_name, email)
        self.db_session.add(reservation)
        self.db_session.flush()

        # map the ME service to the new author
        asm = AuthorServiceMap(author.id, data_access.service.name_to_id('me'))
        self.db_session.add(asm)
        self.db_session.flush()

        # insert the all, of-me, and liked photo albums
        all_photos = ServiceEvent(asm.id,
                                  ServiceObjectType.PHOTO_ALBUM_TYPE,
                                  author.id,
                                  data_access.service.name_to_id('me'),
                                  ServiceEvent.make_well_known_service_event_id(ServiceEvent.ALL_PHOTOS_ID, author.id),
                                  datetime.now())
        self.db_session.add(all_photos)

        ofme_photos = ServiceEvent(asm.id,
                                   ServiceObjectType.PHOTO_ALBUM_TYPE,
                                   author.id,
                                   data_access.service.name_to_id('me'),
                                   ServiceEvent.make_well_known_service_event_id(ServiceEvent.OFME_PHOTOS_ID, author.id),
                                   datetime.now())
        self.db_session.add(ofme_photos)

        liked_photos = ServiceEvent(asm.id,
                                    ServiceObjectType.PHOTO_ALBUM_TYPE,
                                    author.id,
                                    data_access.service.name_to_id('me'),
                                    ServiceEvent.make_well_known_service_event_id(ServiceEvent.LIKED_PHOTOS_ID, author.id),
                                    datetime.now())
        self.db_session.add(liked_photos)

        ''' ??? this might only be temporary ???
            Create a default group (follow) and add the author to that group
            so that author is following themselves.
        '''

        authorGroup = AuthorGroup(author.id, DEFAULT_AUTHOR_GROUP)
        self.db_session.add(authorGroup)
        self.db_session.flush()

        mapping = AuthorGroupMap(authorGroup.id, author.id)
        self.db_session.add(mapping)
        self.db_session.flush()

        ''' Add the new author to the authors access group '''
        groupId, = self.db_session.query(AccessGroup.id).filter_by(group_name=ACCESS_GROUP_AUTHORS).one()
        authorAccessGroupMap = AuthorAccessGroupMap(author.id, groupId)
        self.db_session.add(authorAccessGroupMap)
        self.db_session.flush()

        authorJSON = author.toJSONObject()

        logging.info("create author %s and added to group %s" % (author_name, ACCESS_GROUP_AUTHORS))

      except IntegrityError, e:
        logging.error(e.message)
        self.request.response.status_int = 409
        return {'error': e.message}

      except NoResultFound, e:
        logging.error(e.message)
        self.request.response.status_int = 409
        return {'error': e.message}

    return {'author': authorJSON}

  # DELETE /v1/authors/{authorname}
  #
  # delete existing author
  @view_config(route_name='author.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def authorDelete(self):

    author_name = self.request.matchdict['authorname']

    author = self.db_session.query(Author).filter(Author.author_name == author_name).first()
    if not author:
      self.request.response.status_int = 404
      return {'error': 'unknown author: %s' % author_name}

    self.db_session.delete(author)

    logging.info("deleted author: %s" % author_name)

    return {}

  ##
  ## register user
  ##

  # register a new instance of an app -- web, mobile app, etc.
  @view_config(route_name='author.metrics.visitor.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def authorRegisterUser(self):

    authorname = self.request.matchdict['authorname']
    userid = self.request.matchdict['userID']

    author = self.db_session.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error': 'unknown authorname'}

    return {'author': authorname, 'user_id': userid, 'registered': True}

  @view_config(route_name='author.metrics.visitor.CRUD', request_method='POST', renderer='jsonp', http_cache=0)
  def authorRegisterUsage(self):

    authorname = self.request.matchdict['authorname']
    userid = self.request.matchdict['userID']

    author = self.db_session.query(Author).filter_by(author_name=authorname).first()
    if author == None:
      self.request.response.status_int = 404
      return {'error': 'unknown authorname'}

    return {'author': authorname, 'user_id': userid, 'registered': True}
