'''
Created on May 8, 2012

@author: howard
'''

import json
import hashlib
from abc import (abstractmethod, ABCMeta)
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from mi_schema.models import (ServiceEvent, AuthorServiceMap, Service)


class EventProcessor(object):

  __metaclass__ = ABCMeta

  def __init__(self, service_name, db_session, log):

    self.service_name = service_name
    self.db_session = db_session
    self.log = log

    # get the service-id for this collector's service
    service_id, = self.db_session.query(Service.id).filter(Service.service_name == self.service_name).one()
    self.service_id = service_id

  @abstractmethod
  def get_event_interpreter(self, service_event_json):
    pass

  '''
    Handler method to process service events
  '''
  def process(self, tim_author_id, service_author_id, service_event_json):
#    print 'tim_author_id: %s; service_author_id: %s' % (tim_author_id, service_author_id)
#    print json.dumps(service_event_json, sort_keys=True, indent=2)

    # lookup the author service map for this user/service tuple
    asm_id, = self.db_session.query(AuthorServiceMap.id).filter(and_(AuthorServiceMap.author_id == tim_author_id, AuthorServiceMap.service_id == self.service_id)).one()

    interpreter = self.get_event_interpreter(service_event_json)

    # check for existing update
    existing_event = None
    try:
      existing_event = self.db_session.query(ServiceEvent).filter_by(author_service_map_id=asm_id, event_id=interpreter.get_id()).one()
    except NoResultFound:
      pass

    if existing_event:

      # check for possible update

      # generate checksum for existing json stored in DB
      existing_json = json.dumps(json.loads(existing_event.json), sort_keys=True)
      existing_md5 = hashlib.md5()
      existing_md5.update(existing_json)
      existing_digest = existing_md5.hexdigest()

      # generate checksum for new json
      new_json = json.dumps(service_event_json, sort_keys=True)
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

        self.db_session.flush()
        self.db_session.commit()

      else:
        # skip event
        self.log.debug('Skipping unchanged known event')

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

      service_event = ServiceEvent(asm_id, interpreter.get_id(), interpreter.get_time(), url, caption, content, photo, auxiliary_content, profile_image, json.dumps(service_event_json))
      self.db_session.add(service_event)
      self.db_session.flush()
      self.db_session.commit()
