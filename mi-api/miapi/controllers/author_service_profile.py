'''
Created on Jan 16, 2012

@author: howard
'''
import logging

from pyramid.view import view_config

from mi_schema.models import Service, Author, AuthorServiceMap

from profile_fetchers import profile_fetcher

from miapi.models import DBSession

from miapi import oAuthConfig, service_name_dict

log = logging.getLogger(__name__)


class ServiceProfileController(object):

  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.db_session = DBSession()

  # get the author's profile from the first available service of highest
  # precedence
  @view_config(route_name='author.profile.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def get_profile(self):

    author_name = self.request.matchdict['authorname']

    # get author-id for author_name
    try:
      author_id, = self.db_session.query(Author.id).filter(Author.author_name == author_name).one()
    except:
      self.db_session.rollback()
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    # service profile precedence is: linkedin, facebook, googleplus, twitter, instagram, foursquare

    # get all service mappings for author
    mappings = {}
    for asm in self.db_session.query(AuthorServiceMap).filter_by(author_id=author_id).all():
      mappings[asm.service_id] = asm

    profile_json = None

    for service_id in [Service.LINKEDID_ID,
                       Service.FACEBOOK_ID,
                       Service.GOOGLEPLUS_ID,
                       Service.TWITTER_ID,
                       Service.INSTAGRAM_ID,
                       Service.FOURSQUARE_ID]:
      asm = mappings.get(service_id)
      if asm:
        service_name = service_name_dict[service_id]
        fetcher = profile_fetcher.from_service_name(service_name, oAuthConfig[service_name])
        profile_json = fetcher.get_author_profile(asm.service_author_id, asm)
        break

    self.db_session.commit()

    return profile_json

  # get the author's profile for the specificed service
  @view_config(route_name='author.services.profile', request_method='GET', renderer='jsonp', http_cache=0)
  def get_service_profile(self):

    author_name = self.request.matchdict['authorname']
    service_name = self.request.matchdict['servicename']

    # get author-id for author_name
    try:
      author_id, = self.db_session.query(Author.id).filter(Author.author_name == author_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown author %s' % author_name}

    # get service-id for service_name
    try:
      service_id, = self.db_session.query(Service.id).filter(Service.service_name == service_name).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown service %s' % author_name}

    fetcher = profile_fetcher.from_service_name(service_name, oAuthConfig[service_name])
    if not fetcher:
      self.request.response.status_int = 404
      return {'error': 'profile information is not available for service %s' % service_name}

    try:
      mapping = self.db_session.query(AuthorServiceMap).filter_by(service_id=service_id, author_id=author_id).one()
    except:
      self.request.response.status_int = 404
      return {'error': 'unknown service for author'}

    profile_json = fetcher.get_author_profile(mapping.service_author_id, mapping)

    self.db_session.commit()

    return profile_json
