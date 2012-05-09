'''
Created on May 8, 2012

@author: howard
'''

import json
from event_processor import EventProcessor


class FacebookEventProcessor(EventProcessor):

  def process(self, tim_author_id, service_author_id, service_event_json):
    print 'tim_author_id: %s; service_author_id: %s' % (tim_author_id, service_author_id)
    print json.dumps(service_event_json, sort_keys=True, indent=2)
