'''
Created on Jul 13, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from tim_commons import db

from mi_schema.models import (AuthorReservation)


class AuthorReservationController(object):

  # Constructor
  #
  def __init__(self, request):

    self.request = request
    self.db_session = db.Session()

  # OPTIONS /v1/reservation/{authorname}
  # preflight cross-domain requests
  @view_config(route_name='author.reservation', request_method='OPTIONS', renderer='jsonp', http_cache=0)
  def preflight_crossdomain_access_control(self):

    self.request.response.headers['Access-Control-Allow-Origin'] = '*'
    self.request.response.headers['Access-Control-Allow-Methods'] = 'PUT'
    self.request.response.headers['Access-Control-Max-Age'] = 1209600   # valid for 14 days

  # GET /v1/reservation/{authorname}
  #
  # get an authorname reservation -- check to see if it exists
  #
  @view_config(route_name='author.reservation', request_method='GET', renderer='jsonp', http_cache=0)
  def get_reservation(self):

    author_name = self.request.matchdict['authorname']

    # get author-id for author_name
    try:
      reservation = self.db_session.query(AuthorReservation).filter(AuthorReservation.author_name == author_name).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error': 'unknown author-name %s' % author_name}

    except Exception, e:
      self.request.response.status_int = 500
      return {'error': e.message}

    return {'author_name': reservation.author_name}

  # PUT /v1/reservation/{authorname}
  #
  # put the event highlights for the author
  #
  @view_config(route_name='author.reservation', request_method='PUT', renderer='jsonp', http_cache=0)
  def put_reservation(self):

    author_name = self.request.matchdict['authorname']

    reservation_info = self.request.json_body
    if not reservation_info:
      self.request.response.statue_int = 400
      return {'error': 'missing required property: email'}

    # grab the email
    email = reservation_info.get('email')
    if not email:
      self.request.response.statue_int = 400
      return {'error': 'missing required property: email'}

    # get author-id for author_name
    try:
      reservation = AuthorReservation(author_name, email)
      self.db_session.add(reservation)
      self.db_session.flush()

    except IntegrityError, e:
      logging.error(e.message)
      self.request.response.status_int = 409
      return {'error': e.message}

    return {'author_name': author_name, 'email': email}
