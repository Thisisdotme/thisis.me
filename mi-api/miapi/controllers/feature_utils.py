'''
Created on Apr 24, 2012

@author: howard
'''

from sqlalchemy import (and_)

from mi_schema.models import Author, Feature, AuthorFeatureMap, AuthorFeatureDefault

import miapi.json_renders.feature


def get_author_features(db_session, author_id, request):

  features = []
  for feature, afd in db_session.query(Feature, AuthorFeatureDefault). \
      join(AuthorFeatureMap, Feature.id == AuthorFeatureMap.feature_id). \
      outerjoin(AuthorFeatureDefault, and_(AuthorFeatureMap.author_id == AuthorFeatureDefault.author_id,
                                           AuthorFeatureMap.feature_id == AuthorFeatureDefault.feature_id)). \
      join(Author, AuthorFeatureMap.author_id == author_id). \
      order_by(AuthorFeatureMap.sequence):
    featureJSONObj = miapi.json_renders.feature.to_JSON_dictionary(feature, request)
    if afd:
      featureJSONObj['default'] = True
    features.append(featureJSONObj)

  return features
