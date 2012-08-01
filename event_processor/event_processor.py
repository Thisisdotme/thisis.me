import hashlib
import math
import logging
import datetime

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from mi_schema import models
from tim_commons import json_serializer, db, total_seconds, messages
from data_access import service, service_event, event_scanner_priority
import event_correlator
import event_interpreter


class EventProcessor:
  def __init__(self, service_name, max_priority, min_duration, oauth_config):
    self.service_name = service_name
    self.oauth_config = oauth_config
    self.max_priority = max_priority
    self.min_duration = min_duration

    self.service_id = service.name_to_service[service_name].id
    self.me_service_id = service.name_to_service['me'].id

  def process(
      self,
      tim_author_id,
      service_author_id,
      service_event_id,
      state,
      service_event_json,
      links):

    if state == messages.NOT_FOUND_STATE:
      self.process_not_found(tim_author_id, service_author_id, service_event_id)
    else:
      self.process_current(
          tim_author_id,
          service_author_id,
          service_event_id,
          service_event_json,
          links)

  def process_not_found(self, tim_author_id, service_author_id, service_event_id):
    service_object = service_event.query_service_event(
        tim_author_id,
        self.service_id,
        service_event_id)

    if service_object:
      service_event.delete(service_object.id)

      # do we have any correlated events?
      if service_object.correlation_id:
        correlated_events = service_event.query_correlated_events(
            tim_author_id,
            service_object.correlation_id)

        if not correlated_events:
          # list is empty we should delete the correlation event
          count = service_event.delete_correlation_event(
              self.me_service_id,
              service_object.correlation_id,
              tim_author_id)
          if count != 1:
            logging.error(
                'Delete %s rows for correlation: id = %s, author = %d',
                count,
                service_object.correlation_id,
                tim_author_id)

    delete_scanner_event(service_event_id, service_author_id, self.service_name)

  def process_current(
      self,
      tim_author_id,
      service_author_id,
      service_event_id,
      service_event_json,
      links):
    ''' Handler method to process service events '''
    # lookup the author service map for this user/service tuple
    query = db.Session().query(models.AuthorServiceMap)
    query = query.filter_by(author_id=tim_author_id, service_id=self.service_id)
    asm = query.one()

    interpreter = event_interpreter.create_event_interpreter(
        self.service_name,
        service_event_json,
        asm,
        self.oauth_config)

    # check for existing update
    existing_event = None
    try:
      query = db.Session().query(models.ServiceEvent)
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
        correlation_id, correlation_url = event_correlator.correlate_event(interpreter)

        # update event
        existing_event.json = new_json
        existing_event.caption = interpreter.get_headline()
        existing_event.content = interpreter.get_content()
        existing_event.photo_url = interpreter.get_photo()
        existing_event.auxillary_content = interpreter.get_auxiliary_content()
        if interpreter.get_update_time():
          existing_event.modify_time = interpreter.get_update_time()
        else:
          existing_event.modify_time = datetime.datetime.utcnow()
        existing_event.correlation_id = correlation_id

        event_correlator.correlate_and_update_event(
            correlation_url,
            correlation_id,
            tim_author_id,
            self.me_service_id)

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
      correlation_id, correlation_url = event_correlator.correlate_event(interpreter)

      service_event = models.ServiceEvent(
          asm.id,
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
          json_serializer.dump_string(service_event_json),
          correlation_id=correlation_id)
      db.Session().add(service_event)
      db.Session().flush()

      event_correlator.correlate_and_update_event(
          correlation_url,
          correlation_id,
          tim_author_id,
          self.me_service_id)

    # process any links for this event
    if links:
      for link in links:
        relationship = models.Relationship(
            tim_author_id,
            link['service_id'],
            link['service_event_id'],
            tim_author_id,
            asm.service_id,
            interpreter.get_id())
        try:
          db.Session().add(relationship)
          db.Session().flush()
        except IntegrityError:
          logging.warning("Relationship already exists")

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


def delete_scanner_event(
    service_event_id,
    service_user_id,
    service_name):
  event_id = models.EventScannerPriority.generate_id(
      service_event_id,
      service_user_id,
      service_name)

  count = event_scanner_priority.delete(event_id)
  if count != 1:
    logging.error(
        'Delete %s event scanner priority for event = %s, user = %s, name = %s',
        count,
        service_event_id,
        service_user_id,
        service_name)


def update_scanner(event_updated,
                   service_event_id,
                   service_user_id,
                   service_name,
                   update_time,
                   max_priority,
                   min_duration):
  # Get the scanner state from the database
  event_id = models.EventScannerPriority.generate_id(
      service_event_id,
      service_user_id,
      service_name)
  scanner_event = db.Session().query(models.EventScannerPriority).get(event_id)

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

    scanner_event = models.EventScannerPriority(
        service_event_id,
        service_user_id,
        service_name,
        priority)
    db.Session().add(scanner_event)
