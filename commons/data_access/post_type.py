'''
Created on Jul 17, 2012

@author: howard
'''

from tim_commons import db
from mi_schema import models

id_to_post_type = {}


def id_to_label(type_id):
  return id_to_post_type[type_id].label


def initialize():
  post_types = query_all_post_types()

  for post_type in post_types:
    id_to_post_type[post_type.type_id] = post_type


def query_all_post_types():
  query = db.Session().query(models.ServiceObjectType)
  return query.all()


def mock_initialize():
  for identifier, label in [(1, 'highlight'), (2, 'photo-album'), (3, 'photo')]:
    post_type = models.ServiceObjectType(identifier, label)

    id_to_post_type[post_type.type_id] = post_type
