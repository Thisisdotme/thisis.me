from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

'''
TABLE: author
'''

class Author(Base):
  
  __tablename__ = 'author'
  
  id = Column(Integer, primary_key=True)
  author_name = Column(String(255), unique=True, nullable=False)
  email = Column(String(255), unique=True, nullable=False)
  full_name = Column(String(255))
  password = Column(String(255), nullable=False)

  def __init__(self, authorname, email, fullname, password):
    self.author_name = authorname
    self.email = email
    self.full_name = fullname
    self.password = password
  
  def __repr__(self):
    return "<Author('%s','%s','%s','%s')>" % (self.author_name, self.email, self.full_name, self.password)

  def toJSONObject(self):
    return {'author_id':self.id,'author_name':self.author_name,'email':self.email,'full_name':self.full_name}


'''
TABLE: access_group
'''

class AccessGroup(Base):

  __tablename__ = 'access_group'

  id = Column(Integer,primary_key=True)
  group_name = Column(String(255), unique=True, nullable=False)

  def __init__(self, groupname):
    self.group_name = groupname

  def __repr__(self):
    return "<AccessGroup('%s')>" % (self.group_name)

  def toJSONObject(self):
    return {'access_group_id':self.id,'groupname':self.group_name}
  

'''
TABLE: author_access_group_map
'''

class AuthorAccessGroupMap(Base):
  
  __tablename__ = 'author_access_group_map'

  author_id = Column(Integer, ForeignKey('author.id', ondelete="CASCADE"), primary_key=True, nullable=False)
  group_id = Column(Integer, ForeignKey('access_group.id', ondelete="CASCADE"), primary_key=True, nullable=False)

#  author = relationship("Author", backref=backref('accessGroups', order_by=group_id), cascade="all, delete, delete-orphan", single_parent=True)

  def __init__(self, authorId, groupId):
    self.author_id = authorId
    self.group_id = groupId

  def __repr__(self):
    return "<AuthorGroupMap('%s,%s')>" % (self.author_id,self.group_id)

'''
TABLE: feature
'''

class Feature(Base):
  
  __tablename__ = 'feature'
  
  id = Column(Integer, primary_key=True)

  feature_name = Column(String(255), unique=True, nullable=False)
  
  color_icon_high_res = Column(String(255), nullable=False)
  color_icon_medium_res = Column(String(255), nullable=False)
  color_icon_low_res = Column(String(255), nullable=False)
  mono_icon_high_res = Column(String(255), nullable=False)
  mono_icon_medium_res = Column(String(255), nullable=False)
  mono_icon_low_res = Column(String(255), nullable=False)
  
  def __init__(self, featureName, colorIconHighRes, colorIconMediumRes, colorIconLowRes, monoIconHighRes, monoIconMediumRes, monoIconLowRes):
    self.feature_name = featureName
    self.color_icon_high_res = colorIconHighRes
    self.color_icon_medium_res = colorIconMediumRes
    self.color_icon_low_res = colorIconLowRes
    self.mono_icon_high_res = monoIconHighRes
    self.mono_icon_medium_res = monoIconMediumRes
    self.mono_icon_low_res = monoIconLowRes
  
  def __repr__(self):
    return "<Feature('%s')>" % (self.feature_name)

  def toJSONObject(self):
    return {'feature_id':self.id,'name':self.feature_name}


'''
TABLE: author_feature_map
'''

class AuthorFeatureMap(Base):

  __tablename__ = 'author_feature_map'
  __table_args__ = (UniqueConstraint('author_id', 'feature_id', name='uidx_author_feature_map_1'),{})

  id = Column(Integer, primary_key=True)

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)
  feature_id = Column(Integer, ForeignKey('feature.id', ondelete='CASCADE'), nullable=False)

  access_token = Column(String(255))
  access_token_secret = Column(String(255))
  
  last_update_time = Column(DateTime)
  
  most_recent_event_id = Column(String(255))
  most_recent_event_timestamp = Column(DateTime)
  
  auxillary_data = Column(String(65565))
  
  def __init__(self, authorId, featureId, accessToken, accessTokenSecret, auxillaryData=None):
    self.author_id = authorId
    self.feature_id = featureId
    self.access_token = accessToken
    self.access_token_secret = accessTokenSecret
    self.last_update_time = None
    self.most_recent_event_id = None
    self.most_recent_event_timestamp = None
    self.auxillary_data = auxillaryData
    
  def __repr__(self):
    return "<AuthorFeatureMap('%s,%s')>" % (self.author_id,self.feature_id)


'''
TABLE: author_group

  Defines a group private to the author
  
'''
class AuthorGroup(Base):

  __tablename__ = 'author_group'
  __table_args__ = (UniqueConstraint('author_id', 'group_name', name='uidx_author_group_map_1'),{})

  id = Column(Integer, primary_key=True)

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)

  group_name = Column(String(255), nullable=False)

  def __init__(self, authorId, groupName):
    self.author_id = authorId
    self.group_name = groupName

  def __repr__(self):
    return "<AuthorGroup('%s,%s,%s')>" % (self.id,self.author_id,self.group_name)

  def toJSONObject(self):
    return {'author_id': self.author_id,
            'author_group_id':self.id,
            'group_name':self.group_name}

'''
TABLE: author_group_map

  Maps authors to an author_group
  
'''
class AuthorGroupMap(Base):

  __tablename__ = 'author_group_map'

  author_group_id = Column(Integer, ForeignKey('author_group.id', ondelete='CASCADE'), nullable=False, primary_key=True)
  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False, primary_key=True)

  def __init__(self, authorGroupId, authorId):
    self.author_group_id = authorGroupId
    self.author_id = authorId

  def __repr__(self):
    return "<AuthorGroupMap('%s,%s')>" % (self.author_group_id,self.author_id)

  def toJSONObject(self):
    return {'author_id': self.author_id,
            'author_group_id':self.author_group_id}


'''
TABLE: feature_event
'''

class FeatureEvent(Base):
  
  __tablename__ = 'feature_event'
  __table_args__ = (UniqueConstraint('author_feature_map_id', 'event_id', name='uidx_feature_event_1'),
                    Index('idx_feature_event_2', "author_feature_map_id", "create_time"),
                    Index('idx_feature_event_3', "parent_id", "create_time"),
                    {})
  
  id = Column(Integer, primary_key=True)
  
  parent_id = Column(Integer, ForeignKey('feature_event.id'), nullable=True)
  
  author_feature_map_id = Column(Integer, ForeignKey('author_feature_map.id', ondelete='CASCADE'), nullable=False)

  # added for convenience.  Not sure if we want them long term but they make querying feature_events by feature and
  # author easy and more efficient (no join to author_feature_map)
#  feature_id = Column(Integer, ForeignKey('feature.id'), nullable=False)
#  author_id = Column(Integer, ForeignKey('author.id'), nullable=False)

  event_id = Column(String(255), nullable=False)
  create_time = Column(DateTime, nullable=False)
  
  url = Column(String(1024))

  caption = Column(String(4096))
  content = Column(String(4096))
  photo_url = Column(String(4096))
  
  auxillary_content = Column(String(65565))

  author_profile_image_url = Column(String(1024))

  def __init__(self, authorFeatureMapId, eventId, createTime, url=None, caption=None, content=None, photoURL=None, auxillaryContent=None, authorProfileImageUrl=None):
    self.author_feature_map_id = authorFeatureMapId
    self.event_id = eventId
    self.create_time = createTime
    self.url = url
    self.caption = caption
    self.content = content
    self.photo_url = photoURL
    self.auxillary_content = auxillaryContent
    self.author_profile_image_url = authorProfileImageUrl

  def __repr__(self):
    return "<FeatureEvent('%s,%s,%s,%s,%s,%s,%s,%s')>" % (self.id,self.author_feature_map_id,self.create_time,self.url,self.caption,self.content,self.photo_url,self.auxillary_content)


class FeatureEventJSON(Base):
  
  __tablename__ = 'feature_event_json'
  
  feature_event_id = Column(Integer, ForeignKey('feature_event.id', ondelete='CASCADE'), nullable=False, primary_key=True)

  json = Column(String(65535))

  def __init__(self, featureEventId, json=None):
    self.feature_event_id = featureEventId
    self.json = json

  def __repr__(self):
    return "<FeatureEventJSON('%s,%s')>" % (self.feature_event_id,self.json)


# ???
# ??? WHAT IS THIS USED FOR ???
# ???
class OriginMap(Base):
  
  __tablename__ = 'origin_map'

  feature_name = Column(String(255), nullable=False, primary_key=True)
  origin = Column(String(255), nullable=False, primary_key=True)
  origin_feature_name = Column(String(255), nullable=True)

  def __init__(self, featureName, origin, originFeatureName):
    self.feature_name = featureName
    self.origin = origin
    self.origin_feature_name = originFeatureName

  def __repr__(self):
    return "<OriginMap('%s,%s,%s')>" % (self.feature_name,self.origin,self.origin_feature_name)


'''
TABLE: highlight_type
'''

class HighlightType(Base):
  
  __tablename__ = 'highlight_type'

  id = Column(Integer, primary_key=True)

  label = Column(String(256))

  def __init__(self, label):
    self.label = label

  def __repr__(self):
    return "<HighlightType('%d,%s')>" % (self.id,self.label)


'''
TABLE: highlight
'''

class Highlight(Base):
  
  __tablename__ = 'highlight'
#  __table_args__ = (UniqueConstraint('author_feature_map_id', 'event_id', name='uidx_feature_event_1'),
#                    Index('idx_feature_event_2', "author_feature_map_id", "create_time"),
#                    Index('idx_feature_event_3', "parent_id", "create_time"),
#                    {})

  id = Column(Integer, primary_key=True)
  
  highlight_type_id = Column(Integer, ForeignKey('highlight_type.id', ondelete='CASCADE'))

  feature_event_id = Column(Integer, ForeignKey('feature_event.id', ondelete='CASCADE'))

  weight = Column(Integer)

  caption = Column(String(4096))
  content = Column(String(4096))
  auxillary_content = Column(Text(65565))

  def __init__(self, highlightTypeId, featureEventId, weight, caption=None, content=None, auxillaryContent=None):
    self.highlight_type_id = highlightTypeId
    self.feature_event_id = featureEventId
    self.weight = weight
    self.caption = caption
    self.content = content
    self.auxillary_content = auxillaryContent

  def __repr__(self):
    return "<Highlight('%d,%d,%d,%d,%s,%s,%s')>" % (self.id,self.highlight_type_id,self.feature_event_id,self.weight, self.caption,self.content,self.auxillary_content)


'''
TABLE: highlight
'''

class HighlightFeatureEventMap(Base):
  
  __tablename__ = 'highlight_feature_event_map'

  highlight_id = Column(Integer, ForeignKey('highlight.id', ondelete='CASCADE'), nullable=True, primary_key=True)
  feature_event_id = Column(Integer, ForeignKey('feature_event.id', ondelete='CASCADE'), nullable=True, primary_key=True)

  def __init__(self, highlightId, featureEventId):
    self.highlight_id = highlightId
    self.feature_event_id = featureEventId

  def __repr__(self):
    return "<HighlightFeatureEventMap('%s,%s')>" % (self.highlight_id,self.feature_event_id)
