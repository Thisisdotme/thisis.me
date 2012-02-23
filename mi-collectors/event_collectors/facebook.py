'''
Created on Feb 8, 2012

@author: howard
'''
import json, urllib, urllib2

from mi_schema.models import Author
from mi_model import Event
from time import mktime

from full_collector import FullCollector


class FacebookFullCollector(FullCollector):

  def getFeatureName(self):
    return 'facebook'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(FacebookFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)
    
    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

    fbAuxData = json.loads(afm.auxillary_data)
    fbUserId = fbAuxData['id']

    try:

      traversal = self.beginTraversal(dbSession,afm)
      
      # optimization to request only those since we've last updated
      args = {'access_token':afm.access_token}
      if traversal.baselineLastUpdateTime:
        since =int(mktime(traversal.baselineLastUpdateTime.timetuple()))
        args['since'] = since

      # fetch all the pages /me/feed
      path = oauthConfig['endpoint'] % 'me/feed?%s' % urllib.urlencode(args)

      while path and traversal.totalAccepted < 200:

        try:
          req = urllib2.Request(path)
          res = urllib2.urlopen(req)
          rawJSON = json.loads(res.read())
        except Exception, e:
          self.log.error('error parsing /me/feed')
          self.log.error(e)
          
          # abort for this author but continue on
          path = None
          continue
       
        # process the item
        #print json.dumps(rawJSON, sort_keys=True, indent=2)
        
        # loop termination on various constraints is not exact

        # for element in the feed
        for post in rawJSON['data']:
  
          # currently only interested in 'status' posts from the user
          if post['type'] == 'status' and post['from']['id'] == fbUserId:

            event = Event.FacebookEvent(afm.author_id,post['id'],fbUserId).fromJSON(post)
            self.writeEvent(event, traversal)
    
          # if
        # for
    
        # setup for the next page (if any).  Check that we're not looping ?? do we even need to check ??
        nextPath = rawJSON['paging']['next'] if 'paging' in rawJSON and 'next' in rawJSON['paging'] else None
        path = nextPath if nextPath and nextPath != path else None

      self.endTraversal(traversal,authorName)
      
    except Exception, e:
      self.log.error("****ERROR****")
      self.log.error(e)
      dbSession.rollback()
      raise #continue
