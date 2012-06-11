import hashlib
import sys
import math
import logging
from abc import (abstractmethod, ABCMeta)
import datetime

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import (ServiceEvent, AuthorServiceMap, Service, EventScannerPriority)
from tim_commons import json_serializer
from tim_commons import db
from tim_commons import total_seconds


def from_service_name(service_name, max_priority, min_duration, oauth_config):

  # load the desired module from the event_collectors package
  name = 'event_processors.' + service_name + '_event_processor'
  __import__(name)
  mod = sys.modules[name]

  # retrieve the desired class and instantiate a new instance
  cls = getattr(mod, service_name.capitalize() + "EventProcessor")
  collector = cls(service_name, max_priority, min_duration, oauth_config)

  return collector


class EventProcessor:

  __metaclass__ = ABCMeta

  def __init__(self, service_name, max_priority, min_duration, oauth_config):

    self.service_name = service_name
    self.oauth_config = oauth_config
    self.max_priority = max_priority
    self.min_duration = min_duration

    # get the service-id for this collector's service
    query = db.Session().query(Service.id)
    query = query.filter(Service.service_name == self.service_name)
    self.service_id, = query.one()

  @abstractmethod
  def get_event_interpreter(self, service_event_json, author_service_map, oauth_config):
    pass

  def process(self, tim_author_id, service_author_id, service_event_json):
    ''' Handler method to process service events '''
    # lookup the author service map for this user/service tuple
    query = db.Session().query(AuthorServiceMap)
    query = query.filter(and_(AuthorServiceMap.author_id == tim_author_id,
                              AuthorServiceMap.service_id == self.service_id))
    asm = query.one()

    interpreter = self.get_event_interpreter(service_event_json, asm, self.oauth_config)

    # check for existing update
    existing_event = None
    try:
      query = db.Session().query(ServiceEvent)
      query = query.filter_by(author_service_map_id=asm.id, event_id=interpreter.get_id())
      existing_event = query.one()
    except NoResultFound:
      pass

    event_updated = True
    if existing_event:

      # check for possible update

      # generate checksum for existing json stored in DB
      existing_json = json_serializer.normalize_string(existing_event.json)
      existing_md5 = hashlib.md5()
      existing_md5.update(existing_json)
      existing_digest = existing_md5.hexdigest()

      # generate checksum for new json
      new_json = json_serializer.dump_string(service_event_json)
      new_md5 = hashlib.md5()
      new_md5.update(new_json)
      new_digest = new_md5.hexdigest()

      # if the digests are different then the event has been modified; otherwise
      # just skip it
      if existing_digest != new_digest:

        logging.debug('Updating modified known event')

        # update event
        existing_event.json = new_json
        existing_event.caption = interpreter.get_headline()
        existing_event.content = interpreter.get_content()
        existing_event.photo_url = interpreter.get_photo()
        existing_event.auxillary_content = interpreter.get_auxiliary_content()
        existing_event.modify_time = interpreter.get_update_time() if interpreter.get_update_time() \
                                                                 else datetime.datetime.utcnow()

      else:
        # skip event
        logging.debug('Skipping unchanged known event')
        event_updated = False

    else:

      logging.debug('Adding new unknown event')

      # handle new

      #
      # output to MySQL
      #
      url = interpreter.get_url()
      caption = interpreter.get_headline()
      content = interpreter.get_content()
      photo = interpreter.get_photo()
      auxiliary_content = interpreter.get_auxiliary_content()

      # TODO: Deal with profile image
      profile_image = None

      service_event = ServiceEvent(asm.id,
                                   interpreter.get_type(),
                                   asm.author_id,
                                   asm.service_id,
                                   interpreter.get_id(),
                                   interpreter.get_create_time(),
                                   interpreter.get_update_time(),
                                   url,
                                   caption,
                                   content,
                                   photo,
                                   auxiliary_content,
                                   profile_image,
                                   json_serializer.dump_string(service_event_json))
      db.Session().add(service_event)

    update_time = interpreter.get_update_time()
    if update_time is None:
      update_time = interpreter.get_create_time()
    update_scanner(event_updated,
                   interpreter.get_id(),
                   service_author_id,
                   self.service_name,
                   update_time,
                   self.max_priority,
                   self.min_duration)


def update_scanner(event_updated,
                   service_event_id,
                   service_user_id,
                   service_id,
                   update_time,
                   max_priority,
                   min_duration):
  # Get the scanner state from the database
  event_id = EventScannerPriority.generate_id(service_event_id, service_user_id, service_id)
  scanner_event = db.Session().query(EventScannerPriority).get(event_id)

  if scanner_event is not None:
    if event_updated:
      scanner_event.priority = 0
  else:
    logging.debug('The event update time is %s.', update_time)

    min_duration_in_sec = total_seconds(min_duration)
    event_age = datetime.datetime.utcnow() - update_time
    event_age_in_sec = total_seconds(event_age)
    if event_age_in_sec < 0.0:
      event_age_in_sec = math.fabs(event_age_in_sec)
      if event_age_in_sec > min_duration_in_sec:
        logging.warning('Time clock are out of sync by at least: %s', event_age_in_sec)

    logging.debug('Event is %s seconds old and the mininum duration is %s: %s',
                  event_age_in_sec,
                  min_duration_in_sec,
                  event_age_in_sec / min_duration_in_sec)
    priority = int(math.ceil(math.log(event_age_in_sec / min_duration_in_sec, 2)))
    if priority < 0:
      priority = 0
    elif priority > max_priority:
      priority = max_priority

    scanner_event = EventScannerPriority(service_event_id, service_user_id, service_id, priority)
    db.Session().add(scanner_event)
