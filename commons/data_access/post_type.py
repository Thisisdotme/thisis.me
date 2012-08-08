'''
Created on Jul 17, 2012

@author: howard
'''

from tim_commons import db
from mi_schema import models

id_to_post_type = {}
label_to_post_type = {}


def id_to_label(type_id):
  return id_to_post_type[type_id].label


def label_to_id(label):
  return label_to_post_type[label].type_id


def initialize():
  post_types = query_all_post_types()

  for post_type in post_types:
    db.Session().expunge(post_type)
    id_to_post_type[post_type.type_id] = post_type
    label_to_post_type[post_type.label] = post_type

  # Kinda of a hack! Post type that will never make it to the database
  delete = models.ServiceObjectType(256, 'delete')
  id_to_post_type[delete.type_id] = delete
  label_to_post_type[delete.label] = delete


def query_all_post_types():
  query = db.Session().query(models.ServiceObjectType)
  return query.all()


def mock_initialize():
  for identifier, label in [(1, 'highlight'), (2, 'photo_album'), (3, 'photo')]:
    post_type = models.ServiceObjectType(identifier, label)

    id_to_post_type[post_type.type_id] = post_type
