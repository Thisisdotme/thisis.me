'''
Created on Apr 24, 2012

@author: howard
'''

from sqlalchemy import (and_)

from mi_schema.models import Author, Feature, AuthorFeatureMap, AuthorFeatureDefault

def getAuthorFeatures(dbSession, authorId):

  features = []
  for feature,afd in dbSession.query(Feature,AuthorFeatureDefault). \
      join(AuthorFeatureMap,Feature.id==AuthorFeatureMap.feature_id). \
      outerjoin(AuthorFeatureDefault,and_(AuthorFeatureMap.author_id==AuthorFeatureDefault.author_id,AuthorFeatureMap.feature_id==AuthorFeatureDefault.feature_id)). \
      join(Author,AuthorFeatureMap.author_id==authorId). \
      order_by(AuthorFeatureMap.sequence):
    featureJSONObj = feature.toJSONObject()
    if afd:
      featureJSONObj['default'] = True
    features.append(featureJSONObj)

  return features
