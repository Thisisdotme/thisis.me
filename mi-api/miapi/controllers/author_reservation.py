import logging
import re
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import tim_commons.db
import tim_commons.emailer

from mi_schema.models import (AuthorReservation)

import miapi.resource


def add_views(configuration):
  # Reservations
  configuration.add_view(
      add_reservation,
      context=miapi.resource.Reservations,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # Reservation
  configuration.add_view(
      get_reservation,
      context=miapi.resource.Reservation,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      remove_reservation,
      context=miapi.resource.Reservation,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)


def get_reservation(reservation_context, request):
  author_name = reservation_context.author_name

  # get author-id for author_name
  try:
    query = tim_commons.db.Session().query(AuthorReservation)
    query = query.filter_by(author_name=author_name)
    reservation = query.one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error': 'unknown author-name %s' % author_name}

  except Exception, e:
    request.response.status_int = 500
    return {'error': e.message}

  return {'author_name': reservation.author_name}


def add_reservation(request):
  reservation_info = request.json_body
  if not reservation_info:
    request.response.status_int = 400
    return {'error': 'missing required properties: email, author_name'}

  author_name = reservation_info.get('author_name')
  if author_name is None:
    request.response.status_int = 400
    return {'error': 'missing required property: author_name'}

  # validate author_name syntax: max 16 characters and only alpha-numeric, underscore, and dash
  if len(author_name) > 16:
    request.response.status_int = 400
    return {'error': 'Username is too long.  The username cannot exceed 16 characters in length.'}

  regex = re.compile('^[a-zA-Z0-9_]+$')
  if not regex.match(author_name):
    request.response.status_int = 400
    return {'error': 'Username contains invalid characters.  The username can only contain alpha-numeric characters, underscore (_), and hyphen (-).'}

  # grab the email
  email = reservation_info.get('email')
  if not email:
    request.response.status_int = 400
    return {'error': 'missing required property: email'}

  # get author-id for author_name
  try:
    reservation = AuthorReservation(author_name, email, datetime.now())
    tim_commons.db.Session().add(reservation)
    tim_commons.db.Session().flush()

  except IntegrityError, e:
    logging.error(e.message)
    request.response.status_int = 409
    return {'error': e.message}

  # send confirmation email
  tim_commons.emailer.send_template(
      miapi.tim_config['email'],
      'reservation_confirmation.html',
      'accounts@thisis.me',
      email,
      'Username reservation confirmation',
      {'author_name': author_name})

  return {'author_name': author_name, 'email': email}


def remove_reservation(reservation_context, request):
  author_name = reservation_context.author_name

  reservation_info = request.json_body

  if not reservation_info:
    request.response.status_int = 400
    return {'error': 'missing required property: email'}

  # grab the email
  email = reservation_info.get('email')
  if not email:
    request.response.status_int = 400
    return {'error': 'missing required property: email'}

  # get author-id for author_name
  try:
    query = tim_commons.db.Session().query(AuthorReservation)
    query = query.filter(and_(AuthorReservation.author_name == author_name,
                              AuthorReservation.email == email))
    reservation = query.one()
    tim_commons.db.Session().delete(reservation)
    tim_commons.db.Session().flush()

  except NoResultFound:
    request.response.status_int = 404
    return {'error': 'Unknown author-name/email combination'}

  except Exception, e:
    request.response.status_int = 500
    return {'error': e.message}

  return {'author_name': author_name}
