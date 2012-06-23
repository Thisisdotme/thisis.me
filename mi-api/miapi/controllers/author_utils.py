import calendar

from miapi.models import SimpleDBSession
from mi_schema.models import Author, Service, AuthorServiceMap, ServiceEvent, ServiceObjectType

from miapi import oAuthConfig

from event_collectors.collector_factory import EventCollectorFactory
from tim_commons import json_serializer

from . import get_author_info, get_shared_services


def createServiceEvent(dbSession, request, se, asm, author, serviceName):

  if se.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and se.service_id == Service.ME_ID:
    return None

  sourcesItems = get_shared_services(dbSession, request, se.id, serviceName)

  # collect the pieces of available content
  content = {}
  if se.caption:
    content['label'] = se.caption
  if se.content:
    content['data'] = se.content
  if se.auxillary_content:
    content['auxillary_data'] = json_serializer.load_string(se.auxillary_content)
  if se.url:
    content['url'] = se.url
  if se.photo_url:
    content['photo_url'] = se.photo_url

  author_info = get_author_info(request, asm, author)

  event = {'event_id': se.id,
           'service': serviceName,
           'create_time': calendar.timegm(se.create_time.timetuple()),
           'link': request.route_url('author.query.events.eventId', authorname=author.author_name, eventID=se.id),
           'content': content,
           'author': author_info,
           'sources': {'count': len(sourcesItems), 'items': sourcesItems}}

  return event


def createHighlightEvent(dbSession, request, highlight, se, serviceName, author):

  sourcesItems = [{'service_name': serviceName, 'service_image_url': request.static_url('miapi:img/l/services/color/%s.png' % serviceName)}]

  # determine all the shared sources -- all service_event rows whose parent_id is this service_event
  for sharedFeatureName in dbSession.query(Service.service_name).join(AuthorServiceMap, AuthorServiceMap.service_id == Service.id).join(ServiceEvent, AuthorServiceMap.id == ServiceEvent.author_service_map_id).filter(ServiceEvent.parent_id == se.id).all():
    sourcesItems.append({'service_name': sharedFeatureName, 'service_image_url': request.static_url('miapi:img/l/services/color_by_fn/%s.png' % serviceName)})

  # collect the pieces of available content
  content = {}
  if highlight.content:
    content['label'] = highlight.content

  if se.content:
    content['data'] = se.content
  elif se.caption:
    content['data'] = se.caption

  if se.auxillary_content:
    content['auxillary_data'] = json_serializer.load_string(se.auxillary_content)

  if se.url:
    content['url'] = se.url

  if se.photo_url:
    content['photo_url'] = se.photo_url

  profileImageUrl = se.author_profile_image_url if se.author_profile_image_url else request.static_url('miapi:%s' % 'img/profile_placeholder.png')

  author = {'profile_image_url': profileImageUrl, 'name': author.author_name, 'full_name': author.full_name}

  event = {'event_id': se.id,
           'service': serviceName,
           'create_time': calendar.timegm(se.create_time.timetuple()),
           'link': request.route_url('author.query.events.eventId', authorname=request.matchdict['authorname'], eventID=se.id),
           'content': content,
           'author': author,
           'sources': {'count': len(sourcesItems), 'items': sourcesItems}}

  return event


def serviceBuild(authorName, serviceName, incremental, s3Bucket, aws_access_key, aws_secret_key):

  print("refresh %s serviceEvents for %s" % (authorName, serviceName))

  dbSession = SimpleDBSession()

  # get the service-id for serviceName
  serviceId, = dbSession.query(Service.id).filter(Service.service_name == serviceName).one()

  # get author-id for authorName
  authorId, = dbSession.query(Author.id).filter(Author.author_name == authorName).one()

  mapping = dbSession.query(AuthorServiceMap).filter_by(service_id=serviceId, author_id=authorId).one()

  collector = EventCollectorFactory.get_collector_for(serviceName, s3Bucket, aws_access_key, aws_secret_key)
  if collector:
    collector.build_one(mapping, dbSession, oAuthConfig.get(serviceName), incremental)

  dbSession.close()
