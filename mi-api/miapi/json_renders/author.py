'''
Created on Aug 9, 2012

@author: howard
'''

from sqlalchemy import and_
import sqlalchemy.orm.exc

from tim_commons import db
import mi_schema.models
import data_access.service


def to_JSON_dictionary(self):
  return {'id': self.id,
          'author_name': self.author_name,
          'email': self.email,
          'full_name': self.full_name,
          'template': self.template}


def to_person_fragment_JSON_dictionary(author, author_service_map=None):
  JSON_dict = {'service_name': 'me',
               'id': author.id,
               'name': author.author_name,
               'full_name': author.full_name}
  if not author_service_map:
    try:
      author_service_map = db.Session().query(mi_schema.models.AuthorServiceMap). \
                                        filter(and_(mi_schema.models.AuthorServiceMap.author_id == author.id,
                                                    mi_schema.models.AuthorServiceMap.service_id == data_access.service.name_to_id("me"))). \
                                        one()
    except sqlalchemy.orm.exc.NoResultFound:
      pass

  if author_service_map.profile_image_url:
    JSON_dict['picture'] = {'image_url': author_service_map.profile_image_url}

  return JSON_dict
