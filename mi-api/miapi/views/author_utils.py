'''
Created on Feb 21, 2012

@author: howard
'''

import json
from time import mktime

from miapi.models import SimpleDBSession
from mi_schema.models import Author, Feature, AuthorFeatureMap, FeatureEvent

from miapi import oAuthConfig

from event_collectors.collector_factory import EventCollectorFactory

def createFeatureEvent(dbSession,request,fe,featureName,author):

  sourcesItems = [{'feature_name':featureName,'feature_image_url':request.static_url('miapi:img/l/features/color/%s.png' % featureName)}]

  # determine all the shared sources -- all feature_event rows whose parent_id is this feature_event
  for featureName in dbSession.query(Feature.feature_name).join(AuthorFeatureMap,AuthorFeatureMap.feature_id==Feature.id).join(FeatureEvent,AuthorFeatureMap.id==FeatureEvent.author_feature_map_id).filter(FeatureEvent.parent_id==fe.id).all():
    sourcesItems.append({'feature_name':featureName,'feature_image_url':request.static_url('miapi:img/l/features/color_by_fn/%s.png' % featureName)})
  
  # collect the pieces of available content 
  content = {}
  if fe.caption:
    content['label'] = fe.caption
  if fe.content:
    content['data'] = fe.content
  if fe.auxillary_content:
    content['auxillary_data'] = json.loads(fe.auxillary_content)
  if fe.url:
    content['url'] = fe.url
  if fe.photo_url:
    content['photo_url'] = fe.photo_url

  profileImageUrl = fe.author_profile_image_url if fe.author_profile_image_url else request.static_url('miapi:%s' % 'img/profile_placeholder.png') 
    
  author = {'profile_image_url': profileImageUrl, 'name': author.author_name, 'full_name': author.full_name}
  
  event = {'event_id':fe.id,
           'feature':featureName,
           'create_time':int(mktime(fe.create_time.timetuple())),
           'link':request.route_url('author.query.events.eventId',authorname=request.matchdict['authorname'],eventID=fe.id),
           'content':content,
           'author':author,
           'sources':{'count':len(sourcesItems),'items':sourcesItems}}

  return event


def featureBuild(authorName, featureName, incremental, s3Bucket, aws_access_key, aws_secret_key):

  print("refresh %s featureEvents for %s" % (authorName,featureName))

  dbSession = SimpleDBSession()

  # get the feature-id for featureName
  featureId, = dbSession.query(Feature.id).filter(Feature.feature_name == featureName).one()
  
  # get author-id for authorName
  authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()

  mapping = dbSession.query(AuthorFeatureMap).filter_by(feature_id=featureId,author_id=authorId).one()

  collector = EventCollectorFactory.get_collector_for(featureName,s3Bucket, aws_access_key, aws_secret_key)
  if collector:
    collector.build_one(mapping,dbSession,oAuthConfig.get(featureName),incremental)

  dbSession.close()
  
