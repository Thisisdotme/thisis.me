'''
Created on Feb 8, 2012

@author: howard
'''
import json, urllib, urllib2

from mi_schema.models import Author
from mi_model import Event

from full_collector import FullCollector


USER_ACTIVITY = 'people/me/activities/public'
USER_INFO = 'people/me'

class GooglePlusFullCollector(FullCollector):

  def getFeatureName(self):
    return 'googleplus'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(GooglePlusFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)

    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

#    auxData = json.loads(afm.auxillary_data)
#    userId = auxData['id']

    try:

      # we need to exchange the refresh token for an access token 
      queryArgs = urllib.urlencode([('client_id',oauthConfig['key']),
                                    ('client_secret',oauthConfig['secret']),
                                    ('refresh_token',afm.access_token),
                                    ('grant_type','refresh_token')])
      req = urllib2.Request(oauthConfig['oauth_exchange_url'],queryArgs) 
      res = urllib2.urlopen(req)
      rawJSON = json.loads(res.read())
  
#      print json.dumps(rawJSON, sort_keys=True, indent=2)
   
      accessToken = rawJSON['access_token']

      args = {'access_token':accessToken}

      # setup the url for fetching a page of posts
      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_INFO,urllib.urlencode(args))

      # get a little info from the plus people api
      req = urllib2.Request(url)
      res = urllib2.urlopen(req)
      rawJSON = json.loads(res.read())

      profileImageURL = rawJSON['image']['url'] if rawJSON.has_key('image') and rawJSON['image'].has_key('url') else None 

      traversal = self.beginTraversal(dbSession,afm,profileImageURL)
      
      # optimization to request only those since we've last updated
      args['maxResults'] = 100

      # set args for appropriate for incremental update
#      if traversal.baselineLastUpdateTime:
#        since = int(mktime(traversal.baselineLastUpdateTime.timetuple()))
#        args['min_timestamp'] = since

      # setup the url for fetching a page of posts
      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_ACTIVITY,urllib.urlencode(args))

      while url and traversal.totalAccepted < 200:

        try:
          req = urllib2.Request(url)
          res = urllib2.urlopen(req)
          rawJSON = json.loads(res.read())
        except Exception, e:
          self.log.error('error parsing response from %s' % url)
          self.log.error(e)
          
          # abort for this author but continue on
          url = None
          continue
       
        # process the item
#        print json.dumps(rawJSON, sort_keys=True, indent=2)
        
        # for element in the feed
        for post in rawJSON.get('items',[]):

          if post['kind'] == 'plus#activity':
      
            event = Event.GooglePlusEvent(afm.author_id).fromJSON(post)
            self.writeEvent(event, traversal)
    
          # if
        # for
    
        # setup for the next page (if any)
        nextPage = rawJSON.get('nextPageToken')
        if nextPage:
          args['pageToken'] = nextPage
          url = '%s%s?%s' % (oauthConfig['endpoint'],USER_ACTIVITY,urllib.urlencode(args))
        else:
          url = None

      self.endTraversal(traversal,authorName)
      
    except Exception, e:
      self.log.error('****ERROR****')
      self.log.error('Error occurred processing events for: %s' % authorName)
      self.log.error(e)
      dbSession.rollback()
      raise #continue
