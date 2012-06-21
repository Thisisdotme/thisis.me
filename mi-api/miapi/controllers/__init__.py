import logging
import sys

from tim_commons.json_serializer import load_string

from mi_schema.models import Author, ServiceObjectType, ServiceEvent, Service, Relationship

log = logging.getLogger(__name__)


def get_services(db_session, request, se_id, service_name):

  service_items = [{'service_name':service_name, 'service_image_url':request.static_url('miapi:img/l/services/color/%s.png' % service_name)}]

  # determine all the shared sources -- all service_event rows whose parent_id is this service_event
  for shared_service_name in db_session.query(Service.service_name). \
                                        join(ServiceEvent, ServiceEvent.service_id == ServiceEvent.id). \
                                        filter(ServiceEvent.parent_id == se_id).all():
    service_items.append({'service_name': shared_service_name, 'service_image_url': request.static_url('miapi:img/l/services/color_by_fn/%s.png' % shared_service_name)})

  return service_items


def make_photo_obj(db_session, request, se, service_name):

  services = get_services(db_session, request, se.id, service_name)

  photo = {'type': 'photo', 'id': se.id, 'sources': {'count': len(services), 'items': services}}

  if se.caption:
    photo['tagline'] = se.caption

  if se.service_id == Service.FACEBOOK_ID:

    json_obj = load_string(se.json)

    # for some reason not all facebook photo events have an image property; if
    # it doesn't skip it
    if 'images' not in json_obj:
      log.warning('Skipping Facebook event with no images')
      return None

    # default selection to first image
    selection = json_obj['images'][0]

    # find the minimum width photo above 640
    min_resolution = sys.maxint
    for candidate in json_obj.get('images', []):
      if candidate['width'] > 640:
        selection = candidate if candidate['width'] < min_resolution else selection

    if selection and 'source' in selection:
      photo['url'] = selection['source']
      photo['width'] = selection['width']
      photo['height'] = selection['height']

  elif se.service_id == Service.INSTAGRAM_ID:

    json_obj = load_string(se.json)

    selection = json_obj['images']['standard_resolution']
    photo['url'] = selection['url']
    photo['width'] = selection['width']
    photo['height'] = selection['height']

    if 'location' in json_obj:
      photo['location'] = json_obj['location']

  return photo
