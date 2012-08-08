'''
Created on Feb 22, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy import (and_)

from tim_commons import db

from data_access import service

from mi_schema.models import Author, AuthorGroup, AuthorGroupMap, ServiceEvent, Service, AuthorServiceMap, Highlight, ServiceObjectType

from author_utils import createServiceEvent, createHighlightEvent

log = logging.getLogger(__name__)

#
# AUTHOR GROUP QUERY: query for the highlights/details for a particular group (i.e. following)
#


class AuthorGroupQueryController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
      self.request = request
      self.dbSession = db.Session()

  # GET /v1/authors/{authorname}/groups/{groupname}/highlights
  #
  # get the highlights for the author's group
  #
  @view_config(route_name='author.groups.query.highlights', request_method='GET', renderer='jsonp', http_cache=0)
  def get_highlights(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']

    # get author record authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    # get group record for group name
    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id == author.id,
                                                                  AuthorGroup.group_name == groupName)).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown service %s' % authorName}

    events = []
    for highlight, event, asm, author, serviceName in self.dbSession.query(Highlight, ServiceEvent, AuthorServiceMap, Author, Service.service_name). \
              join(ServiceEvent, Highlight.service_event_id == ServiceEvent.id). \
              join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
              join(AuthorGroupMap, AuthorServiceMap.author_id == AuthorGroupMap.author_id). \
              join(Author, AuthorServiceMap.author_id == Author.id). \
              join(Service, AuthorServiceMap.service_id == Service.id). \
              filter(and_(AuthorGroupMap.author_group_id == authorGroup.id, Highlight.weight > 0)). \
              order_by(Highlight.weight.desc(), ServiceEvent.create_time):
      events.append(createHighlightEvent(self.dbSession, self.request, highlight, event, asm, author, serviceName))

    return {'events': events, 'paging': {'prev': None, 'next': None}}

  # /v1/authors/{authorname}/groups/{groupname}/events
  #
  # get all events for the author's group
  #
  @view_config(route_name='author.groups.query.events', request_method='GET', renderer='jsonp', http_cache=0)
  def get_events(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']

    # get author record for authorName
    try:
      author = self.dbSession.query(Author).filter(Author.author_name == authorName).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % authorName}

    # get group record for groupname
    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id == author.id, AuthorGroup.group_name == groupName)).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown service %s' % authorName}

    events = []
    for event, asm, author in self.dbSession. \
            query(ServiceEvent, AuthorServiceMap, Author). \
            join(AuthorServiceMap, ServiceEvent.author_service_map_id == AuthorServiceMap.id). \
            join(AuthorGroupMap, AuthorServiceMap.author_id == AuthorGroupMap.author_id). \
            join(Author, AuthorServiceMap.author_id == Author.id). \
            filter(AuthorGroupMap.author_group_id == authorGroup.id). \
            filter(ServiceEvent.correlation_id == None). \
            order_by(ServiceEvent.create_time.desc()):

      ''' filter well-known and instagram photo albums so they
          don't appear in the timeline
      '''
      if (event.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and
          (event.service_id == service.name_to_id('me') or
           event.service_id == service.name_to_id('instagram'))):
        continue

      event_obj = createServiceEvent(self.dbSession, self.request, event, asm, author)
      if event_obj:
        events.append(event_obj)

    return {'events': events, 'paging': {'prev': None, 'next': None}}
