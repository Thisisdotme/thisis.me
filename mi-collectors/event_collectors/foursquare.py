'''
Created on Feb 8, 2012

@author: howard
'''
import json, urllib, urllib2

from mi_schema.models import Author

from mi_model import Event

from full_collector import FullCollector

USER_CHECKINS = 'users/self/checkins'

class FoursquareFullCollector(FullCollector):

  def getFeatureName(self):
    return 'foursquare'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(FoursquareFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)

    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

#    auxData = json.loads(afm.auxillary_data)
#    userId = auxData['id']

    try:

      traversal = self.beginTraversal(dbSession,afm)

      # start by getting the first 250 checkin.  For now we won't bother seeding the system
      # with anymore than 250
      # users/self/checkins
      args = {'oauth_token': afm.access_token,
              'v': 20120130,
              'limit':250}
  
      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_CHECKINS,urllib.urlencode(args))

      while url and traversal.totalAccepted < 200:
  
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        try:
          rawJSON = json.loads(res.read())
        except:
          self.log.error('error parsing %s' % USER_CHECKINS)
          continue
    
        if rawJSON['meta']['code'] != 200:
          raise Exception('Foursquare error response: %s' % rawJSON['meta']['code'])
    
        # for element in the feed
        for post in rawJSON['response']['checkins']['items']:
    
          event = Event.FoursquareEvent(afm.author_id,post['id']).fromJSON(post)
          self.writeEvent(event, traversal)
  
        # for
        
        # setup next
        url = None

      self.endTraversal(traversal,authorName)
      
    except Exception, e:
      self.log.error('****ERROR****')
      self.log.error(e)
      dbSession.rollback()
      raise #continue
