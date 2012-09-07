import sqlalchemy.orm.exc

from tim_commons import db
import mi_schema.models
import data_access.service


def to_JSON_dictionary(author, author_service_map=None):
  return to_person_fragment_JSON_dictionary(author, author_service_map)


def append_private_JSON(author, JSON_dict):
  JSON_dict['email'] = author.email
  return JSON_dict


def to_person_fragment_JSON_dictionary(author, author_service_map=None):
  JSON_dict = {'service_name': 'me',
               'id': author.id,
               'name': author.author_name,
               'full_name': author.full_name,
               'template': author.template,
               'tagline': author.tagline}

  if not author_service_map:
    try:
      query = db.Session().query(mi_schema.models.AuthorServiceMap)
      query = query.filter_by(author_id=author.id, service_id=data_access.service.name_to_id("me"))
      author_service_map = query.one()
    except sqlalchemy.orm.exc.NoResultFound:
      pass

  if author_service_map.profile_image_url:
    JSON_dict['picture'] = {'image_url': author_service_map.profile_image_url}

  return JSON_dict
