import hashlib
from abc import (abstractmethod, ABCMeta)
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import (ServiceEvent, AuthorServiceMap, Service, EventScannerPriority)
from tim_commons import json_serializer


class EventProcessor(object):

  __metaclass__ = ABCMeta

  def __init__(self, service_name, db_session, log):

    self.service_name = service_name
    self.db_session = db_session
    self.log = log

    # get the service-id for this collector's service
    query = self.db_session.query(Service.id)
    query.filter(Service.service_name == self.service_name)
    self.service_id = query.one()

  @abstractmethod
  def get_event_interpreter(self, service_event_json):
    pass

  def process(self, tim_author_id, service_author_id, service_event_json):
    ''' Handler method to process service events '''
    # lookup the author service map for this user/service tuple
    query = self.db_session.query(AuthorServiceMap.id)
    query.filter(and_(AuthorServiceMap.author_id == tim_author_id,
                      AuthorServiceMap.service_id == self.service_id))
    asm_id, = query.one()

    interpreter = self.get_event_interpreter(service_event_json)

    # check for existing update
    existing_event = None
    try:
      query = self.db_session.query(ServiceEvent)
      query.filter_by(author_service_map_id=asm_id, event_id=interpreter.get_id())
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

        self.log.debug('Updating modified known event')

        # update event
        existing_event.json = new_json
        existing_event.caption = interpreter.get_headline()
        existing_event.content = interpreter.get_content()
        existing_event.photo_url = interpreter.get_photo()
        existing_event.auxillary_content = interpreter.get_auxiliary_content()
        existing_event.modify_time = datetime.now()

      else:
        # skip event
        self.log.debug('Skipping unchanged known event')
        event_updated = False

    else:

      self.log.debug('Adding new unknown event')

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

      service_event = ServiceEvent(asm_id,
                                   interpreter.get_id(),
                                   interpreter.get_time(),
                                   url,
                                   caption,
                                   content,
                                   photo,
                                   auxiliary_content,
                                   profile_image,
                                   json_serializer.dump_string(service_event_json))
      self.db_session.add(service_event)

    update_scanner(self.db_serssion,
                   event_updated,
                   interpreter.get_id(),
                   service_author_id,
                   self.service_name)

    self.db_session.commit()


def update_scanner(db_session, event_updated, service_event_id, service_user_id, service_id):
  # Get the scanner state from the database
  event_id = EventScannerPriority.generate_id(service_event_id, service_user_id, service_id)
  scanner_event = db_session.query(EventScannerPriority).get(event_id)

  if scanner_event is not None:
    if event_updated:
      scanner_event.priority = 0
    else:
      scanner_event.priority += 1
  else:
    priority = 0 if event_updated else 1
    scanner_event = EventScannerPriority(service_event_id, service_user_id, service_id, priority)
    db_session.add(scanner_event)
