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

  def getServiceName(self):
    return 'facebook'

  # update_author
  def build_one(self,afm,dbSession,oauthConfig,incremental):

    super(FacebookFullCollector, self).build_one(afm,dbSession,oauthConfig,incremental)
    
    # get the name of the author  
    authorName = dbSession.query(Author.author_name).filter_by(id=afm.author_id).one()

    fbAuxData = json.loads(afm.auxillary_data)
    fbUserId = fbAuxData['id']

    try:

      args = {'access_token':afm.access_token}

      # fetch all the pages /me/feed
      path = oauthConfig['endpoint'] % 'me/picture?%s' % urllib.urlencode(args)
      req = urllib2.Request(path)
      res = urllib2.urlopen(req)
      
      profileImageURL = res.geturl()

      traversal = self.beginTraversal(dbSession,afm,profileImageURL)
      
      # optimization to request only those since we've last updated
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
#          if post['type'] == 'status' and post['from']['id'] == fbUserId:
          if post['from']['id'] == fbUserId:

#            # check if I'm in the story tags anywhere.
#            found = False
#            if post.get('type') == 'status' and post.has_key('story_tags'):
#              storyTags = post['story_tags']
#              for tagKey in storyTags:
#                tag = storyTags.get(tagKey)
#                for tagItem in tag:
#                  if tagItem['id'] == fbUserId:
#                    found = True
#            
#            if found:
#              continue

            # if this is a status update and there are no actions then skip it
            if post.get('type') == 'status' and post.get('actions') is None:
              continue

            event = Event.FacebookEvent(afm.author_id,fbUserId).fromJSON(post)
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
