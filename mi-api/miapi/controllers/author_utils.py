import calendar

from tim_commons import json_serializer

from mi_schema.models import ServiceObjectType

from . import (
  get_service_author_fragment,
  get_location_fragment,
  get_post_type_detail_fragment,
  get_tim_author_fragment)

from data_access import post_type


def createServiceEvent(db_session, request, se, asm, author):

  link = request.route_url('author.query.events.eventId',
                           authorname=author.author_name,
                           eventID=se.id)

  # TODO uncomment after correlation event JSON is updated -- for now return None
  # TODO checking for correlation event handling ???
  if se.type_id == ServiceObjectType.CORRELATION_TYPE:
    return None
#    # we just want to return the json after adding the links to it
#    event = json_serializer.load_string(se.json)
#    event['link'] = link
#    event['id'] = se.id
#    event['event_id'] = se.id
#    for source in event['sources']['items']:
#      link = 'miapi:img/l/services/color/{0}.png'.format(source['service_name'])
#      source['link'] = request.static_url(link)

  else:

    event = {'id': se.id,
             'type': post_type.id_to_label(se.type_id),
             'link': link,
             'truncated': False,
             'create_time': calendar.timegm(se.create_time.timetuple()),
             'modify_time': calendar.timegm(se.modify_time.timetuple())}

    if se.headline:
      event['headline'] = se.headline
    else:
      # TODO remove when caption goes away
      if se.caption:
        event['headline'] = se.caption
    if se.tagline:
      event['tagline'] = se.tagline
    if se.content:
      event['content'] = se.content

    if se.photo_url:
      event['photo'] = {'image_url': se.photo_url}
      if se.photo_width:
        event['photo']['width'] = se.photo_width
      if se.photo_height:
        event['photo']['height'] = se.photo_height

    event['author'] = get_tim_author_fragment(request, author.author_name)

    event['origin'] = {}
    event['origin']['known'] = get_service_author_fragment(request, asm, author)

  location = get_location_fragment(se)
  if location:
    event['location'] = location

  post_detail = get_post_type_detail_fragment(db_session, se, author)
  if post_detail:
    event['post_type_detail'] = {}
    event['post_type_detail'][post_type.id_to_label(se.type_id)] = post_detail

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

  author_info = get_service_author_fragment(request, asm, author)

  event = {'id': se.id,
           'event_id': se.id,
           'type': post_type.id_to_label(se.type_id),
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

#  db_session = db.Session()
#
#  # get the service-id for serviceName
#  service_id = db_session.query(Service.id).filter(Service.service_name == serviceName).scalar()
#
#  # get author-id for authorName
#  author_id = db_session.query(Author.id).filter(Author.author_name == authorName).scalar()
