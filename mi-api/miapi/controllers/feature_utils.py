'''
Created on Apr 24, 2012

@author: howard
'''

from mi_schema.models import Author, Feature, AuthorFeatureMap

def getAuthorFeatures(dbSession, authorId):

  features = []
  for feature in dbSession.query(Feature).join(AuthorFeatureMap).filter(Feature.id==AuthorFeatureMap.feature_id).join(Author).filter(AuthorFeatureMap.author_id==authorId).order_by(AuthorFeatureMap.sequence):
    features.append(feature.toJSONObject())

  return features
