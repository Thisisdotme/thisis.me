from sqlalchemy import (and_)

import tim_commons.db
from mi_schema.models import Author, Feature, AuthorFeatureMap, AuthorFeatureDefault

import miapi.json_renders.feature


def get_author_features(author_id, request):
  query = tim_commons.db.Session().query(Feature, AuthorFeatureDefault)
  query = query.join(AuthorFeatureMap, Feature.id == AuthorFeatureMap.feature_id)
  query = query.outerjoin(
      AuthorFeatureDefault,
      and_(
        AuthorFeatureMap.author_id == AuthorFeatureDefault.author_id,
        AuthorFeatureMap.feature_id == AuthorFeatureDefault.feature_id))
  query = query.join(Author, AuthorFeatureMap.author_id == author_id)
  query = query.order_by(AuthorFeatureMap.sequence)

  features = []
  for feature, afd in query:
    featureJSONObj = miapi.json_renders.feature.to_JSON_dictionary(feature, request)
    if afd:
      featureJSONObj['default'] = True
    features.append(featureJSONObj)

  return features
