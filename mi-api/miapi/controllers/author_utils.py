'''
Created on Feb 21, 2012

@author: howard
'''

import json
from time import mktime

from miapi.models import SimpleDBSession
from mi_schema.models import Author, Service, AuthorServiceMap, ServiceEvent

from miapi import oAuthConfig

from event_collectors.collector_factory import EventCollectorFactory

def createServiceEvent(dbSession,request,fe,serviceName,author):

  sourcesItems = [{'service_name':serviceName,'service_image_url':request.static_url('miapi:img/l/services/color/%s.png' % serviceName)}]

  # determine all the shared sources -- all service_event rows whose parent_id is this service_event
  for sharedFeatureName in dbSession.query(Service.service_name).join(AuthorServiceMap,AuthorServiceMap.service_id==Service.id).join(ServiceEvent,AuthorServiceMap.id==ServiceEvent.author_service_map_id).filter(ServiceEvent.parent_id==fe.id).all():
    sourcesItems.append({'service_name':sharedFeatureName,'service_image_url':request.static_url('miapi:img/l/services/color_by_fn/%s.png' % serviceName)})
  
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
           'service':serviceName,
           'create_time':int(mktime(fe.create_time.timetuple())),
           'link':request.route_url('author.query.events.eventId',authorname=request.matchdict['authorname'],eventID=fe.id),
           'content':content,
           'author':author,
           'sources':{'count':len(sourcesItems),'items':sourcesItems}}

  return event


def createHighlightEvent(dbSession,request,highlight,fe,serviceName,author):

  sourcesItems = [{'service_name':serviceName,'service_image_url':request.static_url('miapi:img/l/services/color/%s.png' % serviceName)}]

  # determine all the shared sources -- all service_event rows whose parent_id is this service_event
  for sharedFeatureName in dbSession.query(Service.service_name).join(AuthorServiceMap,AuthorServiceMap.service_id==Service.id).join(ServiceEvent,AuthorServiceMap.id==ServiceEvent.author_service_map_id).filter(ServiceEvent.parent_id==fe.id).all():
    sourcesItems.append({'service_name':sharedFeatureName,'service_image_url':request.static_url('miapi:img/l/services/color_by_fn/%s.png' % serviceName)})
  
  # collect the pieces of available content 
  content = {}
  if highlight.content:
    content['label'] = highlight.content

  if fe.content:
    content['data'] = fe.content
  elif fe.caption:
    content['data'] = fe.caption

  if fe.auxillary_content:
    content['auxillary_data'] = json.loads(fe.auxillary_content)

  if fe.url:
    content['url'] = fe.url

  if fe.photo_url:
    content['photo_url'] = fe.photo_url

  profileImageUrl = fe.author_profile_image_url if fe.author_profile_image_url else request.static_url('miapi:%s' % 'img/profile_placeholder.png') 
    
  author = {'profile_image_url': profileImageUrl, 'name': author.author_name, 'full_name': author.full_name}
  
  event = {'event_id':fe.id,
           'service':serviceName,
           'create_time':int(mktime(fe.create_time.timetuple())),
           'link':request.route_url('author.query.events.eventId',authorname=request.matchdict['authorname'],eventID=fe.id),
           'content':content,
           'author':author,
           'sources':{'count':len(sourcesItems),'items':sourcesItems}}

  return event


def serviceBuild(authorName, serviceName, incremental, s3Bucket, aws_access_key, aws_secret_key):

  print("refresh %s serviceEvents for %s" % (authorName,serviceName))

  dbSession = SimpleDBSession()

  # get the service-id for serviceName
  serviceId, = dbSession.query(Service.id).filter(Service.service_name == serviceName).one()
  
  # get author-id for authorName
  authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()

  mapping = dbSession.query(AuthorServiceMap).filter_by(service_id=serviceId,author_id=authorId).one()

  collector = EventCollectorFactory.get_collector_for(serviceName,s3Bucket, aws_access_key, aws_secret_key)
  if collector:
    collector.build_one(mapping,dbSession,oAuthConfig.get(serviceName),incremental)

  dbSession.close()
  
