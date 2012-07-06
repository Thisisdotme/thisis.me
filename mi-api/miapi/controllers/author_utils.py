import calendar

from tim_commons import db

from mi_schema.models import Author, Service, ServiceObjectType

from tim_commons import json_serializer

from miapi import service_object_type_dict

from . import get_author_info


def createServiceEvent(db_session, request, se, asm, author):

  # filter well-known and instagram photo albums
  if (se.type_id == ServiceObjectType.PHOTO_ALBUM_TYPE and
      (se.service_id == Service.ME_ID or se.service_id == Service.INSTAGRAM_ID)):
    return None

  link = request.route_url('author.query.events.eventId',
                           authorname=author.author_name,
                           eventID=se.id)

  if se.service_id == Service.ME_ID and se.json != 'null':
    # we just want to return the json after adding the links to it
    event = json_serializer.load_string(se.json)
    event['link'] = link
    event['id'] = se.id
    event['event_id'] = se.id
    for source in event['sources']['items']:
      link = 'miapi:img/l/services/color/{0}.png'.format(source['service_name'])
      source['link'] = request.static_url(link)

  else:
    # construct the json
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

    event = {'id': se.id,
             'event_id': se.id,   # TODO deprecated -- remove after eliminating from UI
             'type': service_object_type_dict[se.type_id],
             'service': Service.id_to_name[se.service_id],
             'create_time': calendar.timegm(se.create_time.timetuple()),
             'modify_time': calendar.timegm(se.modify_time.timetuple()),
             'link': link,
             'content': content,
             'author': author_info,
             'sources': {'count': 0, 'items': []}}

  return event


def createHighlightEvent(db_session, request, highlight, se, asm, author, serviceName):

  # TODO: fix this: sourcesItems = get_shared_services(db_session, request, se.id, serviceName)

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

  author_info = get_author_info(request, asm, author)

  event = {'id': se.id,
           'event_id': se.id,
           'type': service_object_type_dict[se.type_id],
           'service': serviceName,
           'create_time': calendar.timegm(se.create_time.timetuple()),
           'modify_time': calendar.timegm(se.modify_time.timetuple()),
           'link': request.route_url('author.query.events.eventId',
                                     authorname=request.matchdict['authorname'],
                                     eventID=se.id),
           'content': content,
           'author': author_info}
  # TODO: fix this: 'sources': {'count': len(sourcesItems), 'items': sourcesItems}}

  return event


def serviceBuild(authorName, serviceName, incremental, s3Bucket, aws_access_key, aws_secret_key):

  print("refresh %s serviceEvents for %s" % (authorName, serviceName))

  db_session = db.Session()

  # get the service-id for serviceName
  serviceId, = db_session.query(Service.id).filter(Service.service_name == serviceName).one()

  # get author-id for authorName
  authorId, = db_session.query(Author.id).filter(Author.author_name == authorName).one()

  db_session.close()
