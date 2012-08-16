import calendar
import logging


import data_access.post_type
import data_access.author_service_map
import data_access.service
import tim_commons.db
import tim_commons.json_serializer

import miapi.controllers


def createServiceEvent(request, se, me_asm, asm, author):
  event = {'id': se.id,
           'type': data_access.post_type.id_to_label(se.type_id),
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

  author_info = miapi.controllers.get_service_author_fragment(request, me_asm, author)
  event['author'] = author_info

  location = miapi.controllers.get_location_fragment(se)
  if location:
    event['location'] = location

  post_detail = miapi.controllers.get_post_type_detail_fragment(
      tim_commons.db.Session(),
      se,
      author)
  if post_detail:
    event['post_type_detail'] = {}
    event['post_type_detail'][data_access.post_type.id_to_label(se.type_id)] = post_detail

  if data_access.post_type.id_to_post_type[se.type_id].label == 'correlation':
    json = tim_commons.json_serializer.load_string(se.json)
    # Set the source
    if json['origin']['type'] == 'known':
      known = json['origin']['known']

      event['origin'] = {'type': 'known',
                         'known': {'event_id': known['event_id'],
                                   'service_name': known['service_name'],
                                   'service_event_id': known['service_event_id'],
                                   'service_event_url': known['service_event_url'],
                                   'service_user': miapi.controllers.get_service_author_fragment(
                                       request,
                                       asm,
                                       author)}}
    elif json['origin']['type'] == 'unknown':
      unknown = json['origin']['unknown']
      event['origin'] = {'type': 'unknown',
                         'unknown': {'domain': unknown['domain'],
                                     'small_icon': unknown['small_icon'],
                                     'url': unknown['url']}}
    else:
      logging.error('Found correlation type with malformated origin: %s', json)

    event['shares'] = [{
      'event_id': share['event_id'],
      'service_name': share['service_name'],
      'service_event_id': share['service_event_id'],
      'service_event_url': share['service_event_url'],
      'service_user': miapi.controllers.get_service_author_fragment(
          request,
          data_access.author_service_map.query_asm_by_author_and_service(
            share['author_id'],
            share['service_id']),
          author)}
      for share in json['shares']]
  else:
    event['origin'] = {'type': 'known',
                       'known': {'event_id': se.id,
                                 'service_name': data_access.service.id_to_name(se.service_id),
                                 'service_event_id': se.event_id,
                                 'service_event_url': se.url,
                                 'service_user': miapi.controllers.get_service_author_fragment(
                                     request,
                                     asm,
                                     author)}}

  return event


'''
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
'''
