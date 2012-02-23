'''
Created on Jan 3, 2012

@author: howard
'''

from abc import abstractmethod

from mi_schema.models import Feature
from mi_schema.models import AuthorFeatureMap
from mi_schema.models import Author

'''
This is the superclass for all collectors.  It provides a common infrastructure for all collectors
'''
class Collector(object):
  '''
  classdocs
  '''
  featureName = None
  
  '''
  Constructor
  '''
  def __init__(self):
    print '%s collector executing...' % self.featureName 

  '''
  updateAll
    queries DB for all users that have feature installed and call updateAuthor for each
  '''
  def update_all(self,dbSession,oauthConfig):
    
    # get the feature-id for this feature
    featureId, = dbSession.query(Feature.id).filter_by(feature_name=self.featureName).first()

    # query the db for all users that have the feature installed
    for featureMap in dbSession.query(AuthorFeatureMap).filter_by(feature_id=featureId).all():

      # get the name of the author  
      authorName, = dbSession.query(Author.author_name).filter_by(id=featureMap.author_id).first()
  
      print 'querying %s for author "%s"' % (self.featureName,authorName)
  
      self.update_author(featureMap,dbSession,oauthConfig)

  @abstractmethod
  def update_author(self,featureMap,dbSession,oauthConfig):
    pass