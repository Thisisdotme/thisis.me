'''
Created on Feb 8, 2012

@author: howard
'''
import json
import urllib
import oauth2 as oauth
from datetime import timedelta
from time import mktime

from tim_commons.oauth import make_request
from mi_schema.models import Author

from full_collector import FullCollector
from mi_model.Event import LinkedInEvent


FULL_LOOKBACK_WINDOW = timedelta(days=365)

PAGE_SIZE = 200


class LinkedInFullCollector(FullCollector):

  def getServiceName(self):
    return 'linkedin'

  # update_author
  def build_one(self, afm, dbSession, oauthConfig, incremental):

    super(LinkedInFullCollector, self).build_one(afm, dbSession, oauthConfig, incremental)

    # get the name of the author
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

    auxData = json.loads(afm.auxillary_data)
    userId = auxData['id']

    # setup what we need for oauth
    consumer = oauth.Consumer(oauthConfig['key'], oauthConfig['secret'])
    token = oauth.Token(key=afm.access_token, secret=afm.access_token_secret)
    client = oauth.Client(consumer, token)

    try:

      # request the user's profile
      response = make_request(client, 'http://api.linkedin.com/v1/people/~:(picture-url)', {'x-li-format': 'json'})
      respJSON = json.loads(response)

      profileImageURL = respJSON['pictureUrl'] if 'pictureUrl' in respJSON else None

      traversal = self.beginTraversal(dbSession, afm, profileImageURL)

      # optimization to request only those since we've last updated
      args = {'scope': 'self',
              'type': ['APPS', 'CMPY', 'CONN', 'JOBS', 'JGRP', 'PICT', 'PRFX', 'RECU', 'PRFU', 'QSTN', 'SHAR', 'VIRL'],
              'count': PAGE_SIZE}

      # incremental
      if traversal.baselineLastUpdateTime:
        # since a little before the last update time
        args['after'] = '%s000' % int(mktime(traversal.baselineLastUpdateTime.timetuple()))
      # full
      else:
        # limit to only one year of data
        args['after'] = '%s000' % int(mktime((traversal.now - FULL_LOOKBACK_WINDOW).timetuple()))

      offset = 0
#      args['start'] = offset

      url = '%s?%s' % ('http://api.linkedin.com/v1/people/~/network/updates', urllib.urlencode(args, True))

      while url and traversal.totalAccepted < 200:

        # request the user's updates
        content = make_request(client, url, {'x-li-format': 'json'})

        try:
          rawJSON = json.loads(content)
        except:
          self.log.error('***ERROR*** parse error')
          self.log.error(content)
          continue

#        print json.dumps(rawJSON, sort_keys=True, indent=2)

        if rawJSON.get('_total', 0) == 0:
          url = None
          continue

        LinkedInEvent.eventsFromJSON(self, rawJSON, traversal, afm.author_id, userId, client)

        # setup for the next page (if any)
        if rawJSON['_total'] < PAGE_SIZE:
          url = None
        else:
          offset = offset + PAGE_SIZE
#          args['start'] = offset
          url = '%s?%s' % ('http://api.linkedin.com/v1/people/~/network/updates', urllib.urlencode(args, True))

      self.endTraversal(traversal, authorName)

    except Exception, e:
      self.log.error('****ERROR****')
      self.log.error(e)
      dbSession.rollback()
      raise  # continue
