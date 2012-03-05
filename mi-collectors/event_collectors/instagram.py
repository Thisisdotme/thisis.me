'''
Created on Feb 8, 2012

@author: howard
'''
import json, urllib, urllib2

from mi_schema.models import Author
from mi_model import Event
from time import mktime

from full_collector import FullCollector

USER_INFO = 'users/self'
USER_MEDIA = 'users/self/media/recent'

class InstagramFullCollector(FullCollector):

  def getFeatureName(self):
    return 'instagram'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(InstagramFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)

    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

#    auxData = json.loads(afm.auxillary_data)
#    userId = auxData['id']

    try:

      args = {'access_token':afm.access_token}

      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_INFO,urllib.urlencode(args))
      req = urllib2.Request(url)
      res = urllib2.urlopen(req)
      rawJSON = json.loads(res.read())
      
      profileImageURL = rawJSON['data']['profile_picture'] if rawJSON.has_key('data') and rawJSON['data'].has_key('profile_picture') else None

      traversal = self.beginTraversal(dbSession,afm,profileImageURL)
      
      # optimization to request only those since we've last updated
      args['count'] = 200

      # set args for appropriate for incremental update
      if traversal.baselineLastUpdateTime:
        since = int(mktime(traversal.baselineLastUpdateTime.timetuple()))
        args['min_timestamp'] = since

      # setup the url for fetching a page of posts
      url = '%s%s?%s' % (oauthConfig['endpoint'],USER_MEDIA,urllib.urlencode(args))

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
        for post in rawJSON.get('data',[]):

            event = Event.InstagramEvent(afm.author_id,post['id']).fromJSON(post)
            self.writeEvent(event, traversal)
    
          # if
        # for
    
        # setup for the next page (if any)
        url = rawJSON['pagination']['next_url'] if 'pagination' in rawJSON and 'next_url' in rawJSON['pagination'] else None

      self.endTraversal(traversal,authorName)
      
    except Exception, e:
      self.log.error("****ERROR****")
      self.log.error(e)
      dbSession.rollback()
      raise #continue
