'''
Created on Feb 21, 2012

@author: howard
'''

import json
from time import mktime

from miapi.models import SimpleDBSession
from mi_schema.models import Author, Feature, AuthorFeatureMap

from miapi import oAuthConfig

from event_collectors.collector_factory import EventCollectorFactory

def createFeatureEvent(request,fe,featureName):

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

  event = {'event_id':fe.id,
           'feature':featureName,
           'create_time':int(mktime(fe.create_time.timetuple())),
           'link':request.route_url('author.query.events.eventId',authorname=request.matchdict['authorname'],eventID=fe.id),
           'content':content}

  return event


def featureBuild(authorName, featureName, incremental, aws_access_key, aws_secret_key):

  print("refresh %s featureEvents for %s" % (authorName,featureName))

  dbSession = SimpleDBSession()

  # get the feature-id for featureName
  featureId, = dbSession.query(Feature.id).filter(Feature.feature_name == featureName).one()
  
  # get author-id for authorName
  authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()

  mapping = dbSession.query(AuthorFeatureMap).filter_by(feature_id=featureId,author_id=authorId).one()

  collector = EventCollectorFactory.get_collector_for(featureName,aws_access_key, aws_secret_key)
  if collector:
    collector.build_one(mapping,dbSession,oAuthConfig.get(featureName),incremental)

  dbSession.close()
  
