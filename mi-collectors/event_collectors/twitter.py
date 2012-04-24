'''
Created on Feb 8, 2012

@author: howard
'''
import json, urllib
import oauth2 as oauth

from mi_utils.oauth import make_request
from mi_schema.models import Author

from mi_model import Event

from full_collector import FullCollector

USER_INFO = 'account/verify_credentials.json'
USER_TIMELINE = 'statuses/user_timeline.json'

class TwitterFullCollector(FullCollector):

  def getServiceName(self):
    return 'twitter'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(TwitterFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)

    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

    consumer = oauth.Consumer(oauthConfig['key'], oauthConfig['secret'])
    token = oauth.Token(afm.access_token, afm.access_token_secret)
    
    client = oauth.Client(consumer, token)

    auxData = json.loads(afm.auxillary_data)
    userId = int(auxData['id'])

    try:
  
      # API endpoing for querying user info
      url = '%s%s' % (oauthConfig['endpoint'],USER_INFO)
      userInfoJSON = json.loads(make_request(client,url))
  
      twitterUserId = userInfoJSON['id']
      
      if twitterUserId != userId:
        raise Exception("Bad state - mis-matched twitter user ids")

      profileImageUrl = userInfoJSON['profile_image_url'] if userInfoJSON.has_key('profile_image_url') else None 

      traversal = self.beginTraversal(dbSession,afm,profileImageUrl)
      page = 1

      # API endpoint for getting user timeline
      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_TIMELINE,urllib.urlencode({'include_rts':'1','include_entities':'1','count':'200','page':page}))

      while url and traversal.totalAccepted < 200:

        content = make_request(client,url)
        
        try:
          rawJSON = json.loads(content)
        except:
          self.log.error('***ERROR*** parse error')
          self.log.error(content)
          continue

        if len(rawJSON) == 0:
          url = None
          continue

        for post in rawJSON:
  
          # process the item
          #print json.dumps(post, sort_keys=True, indent=2)
  
          event = Event.TwitterEvent(afm.author_id).fromJSON(post)
  
          self.writeEvent(event,traversal)
      
        # setup for the next page (if any)
        page = page + 1
        url = '%s%s?%s' % (oauthConfig['endpoint'],USER_TIMELINE,urllib.urlencode({'include_rts':'1','include_entities':'1','count':'200','page':page}))

      self.endTraversal(traversal,authorName)
      
    except Exception, e:
      self.log.error('****ERROR****')
      self.log.error(e)
      dbSession.rollback()
      raise #continue
