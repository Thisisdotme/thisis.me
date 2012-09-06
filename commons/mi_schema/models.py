import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    and_)

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm.exc

from tim_commons import db

Base = declarative_base()


class Author(Base):

  __tablename__ = 'author'

  id = Column(Integer, primary_key=True)
  author_name = Column(String(255), unique=True, nullable=False)
  email = Column(String(255), unique=True, nullable=False)
  full_name = Column(String(255))
  password = Column(String(255), nullable=False)
  template = Column(String(255), nullable=True)

  def __init__(self, authorname, email, fullname, password, template):
    self.author_name = authorname
    self.email = email
    self.full_name = fullname
    self.password = password
    self.template = template

  def __repr__(self):
    return "<Author('%s','%s','%s','%s','%s')>" % (self.author_name,
                                                   self.email,
                                                   self.full_name,
                                                   self.password,
                                                   self.template)

  def to_JSON_dictionary(self):
    return {'id': self.id,
            'author_name': self.author_name,
            'email': self.email,
            'full_name': self.full_name,
            'template': self.template}


class AuthorReservation(Base):

  __tablename__ = 'author_reservation'

  author_name = Column(String(255), primary_key=True, nullable=False)
  email = Column(String(255), unique=True, nullable=False)
  create_time = Column(DateTime, nullable=False)

  def __init__(self, authorname, email, create_time=None):
    self.author_name = authorname
    self.email = email
    self.create_time = datetime.datetime.utcnow() if create_time is None else create_time

  def __repr__(self):
    return '<AuthorReservation(\'{0}\',\'{1}\',\'{2}\')>'.format(self.author_name,
                                                                 self.email,
                                                                 self.create_time)


class Service(Base):

  __tablename__ = 'service'

  id = Column(Integer, primary_key=True)

  service_name = Column(String(255), unique=True, nullable=False)

  color_icon_high_res = Column(String(255), nullable=False)
  color_icon_medium_res = Column(String(255), nullable=False)
  color_icon_low_res = Column(String(255), nullable=False)
  mono_icon_high_res = Column(String(255), nullable=False)
  mono_icon_medium_res = Column(String(255), nullable=False)
  mono_icon_low_res = Column(String(255), nullable=False)

  def __init__(self,
               serviceName,
               colorIconHighRes,
               colorIconMediumRes,
               colorIconLowRes,
               monoIconHighRes,
               monoIconMediumRes,
               monoIconLowRes):
    self.service_name = serviceName
    self.color_icon_high_res = colorIconHighRes
    self.color_icon_medium_res = colorIconMediumRes
    self.color_icon_low_res = colorIconLowRes
    self.mono_icon_high_res = monoIconHighRes
    self.mono_icon_medium_res = monoIconMediumRes
    self.mono_icon_low_res = monoIconLowRes

  def __repr__(self):
    return "<Service('%s')>" % (self.service_name)

  @classmethod
  def exists(cls, service_name):
    return db.Session().query(Service).filter(Service.service_name == service_name).count() == 1


class AuthorServiceMap(Base):

  __tablename__ = 'author_service_map'
  __table_args__ = (UniqueConstraint('author_id', 'service_id', name='uidx_author_service_map_1'),
                    UniqueConstraint('service_id', 'service_author_id', name='uidx_author_service_map_2'),
                    {})

  id = Column(Integer, primary_key=True)

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)
  service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)

  service_author_id = Column(String(255))

  access_token = Column(String(255))
  access_token_secret = Column(String(255))

  last_update_time = Column(DateTime)

  most_recent_event_id = Column(String(255))
  most_recent_event_timestamp = Column(DateTime)

  profile_image_url = Column(String(1024))

  def __init__(self, authorId, serviceId, accessToken=None, accessTokenSecret=None, service_author_id=None):
    self.author_id = authorId
    self.service_id = serviceId
    self.access_token = accessToken
    self.access_token_secret = accessTokenSecret
    self.last_update_time = None
    self.most_recent_event_id = None
    self.most_recent_event_timestamp = None
    self.service_author_id = service_author_id

  def __repr__(self):
    return "<AuthorServiceMap('%s,%s')>" % (self.author_id, self.service_id)


class AuthorGroup(Base):

  __tablename__ = 'author_group'
  __table_args__ = (UniqueConstraint('author_id', 'group_name', name='uidx_author_group_map_1'),
                    {})

  id = Column(Integer, primary_key=True)

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)

  group_name = Column(String(255), nullable=False)

  def __init__(self, authorId, groupName):
    self.author_id = authorId
    self.group_name = groupName

  def __repr__(self):
    return "<AuthorGroup('%s,%s,%s')>" % (self.id, self.author_id, self.group_name)

  @classmethod
  def exists(cls, author_id, group_name):
    return db.Session().query(AuthorGroup).filter(and_(AuthorGroup.author_id == author_id,
                                                       AuthorGroup.group_name == group_name)).count() == 1

  @classmethod
  def lookup(cls, author_id, group_name):
    author_group = None
    try:
      author_group = db.Session().query(AuthorGroup). \
                                  filter(and_(AuthorGroup.author_id == author_id,
                                              AuthorGroup.group_name == group_name)).one()

    except sqlalchemy.orm.exc.NoResultFound:
      pass

    return author_group

  def to_JSON_dictionary(self):
    return {'id': self.id,
            'group_name': self.group_name}


class AuthorGroupMap(Base):

  __tablename__ = 'author_group_map'

  author_group_id = Column(Integer,
                           ForeignKey('author_group.id', ondelete='CASCADE'),
                           nullable=False,
                           primary_key=True)
  author_id = Column(Integer,
                     ForeignKey('author.id', ondelete='CASCADE'),
                     nullable=False,
                     primary_key=True)

  def __init__(self, authorGroupId, authorId):
    self.author_group_id = authorGroupId
    self.author_id = authorId

  def __repr__(self):
    return "<AuthorGroupMap('%s,%s')>" % (self.author_group_id, self.author_id)

  @classmethod
  def exists(cls, author_id, group_name, member):
    return db.Session().query(AuthorGroupMap). \
                        join(AuthorGroup, AuthorGroupMap.author_group_id == AuthorGroup.id). \
                        join(Author, AuthorGroupMap.author_id == Author.id). \
                        filter(AuthorGroup.author_id == author_id). \
                        filter(AuthorGroup.group_name == group_name). \
                        filter(Author.author_name == member). \
                        count() == 1

  @classmethod
  def lookup(cls, author_id, group_name, member):
    author_group_member = None
    try:
      author_group_member = db.Session().query(AuthorGroupMap). \
                          join(AuthorGroup, AuthorGroupMap.author_group_id == AuthorGroup.id). \
                          join(Author, AuthorGroupMap.author_id == Author.id). \
                          filter(AuthorGroup.author_id == author_id). \
                          filter(AuthorGroup.group_name == group_name). \
                          filter(Author.author_name == member). \
                          one()

    except sqlalchemy.orm.exc.NoResultFound:
      pass

    return author_group_member

  def to_JSON_dictionary(self, author, group):
    # lookup the member author info
    member_author = db.Session().query(Author).get(self.author_id)

    return {'author_name': author.author_name,
            'id': author.id,
            'group': group.to_JSON_dictionary(),
            'member': member_author.to_JSON_dictionary()}


class ServiceObjectType(Base):

  __tablename__ = 'service_object_type'

  type_id = Column(Integer, primary_key=True)

  label = Column(String(255), nullable=False)

  HIGHLIGHT_TYPE = 1
  PHOTO_ALBUM_TYPE = 2
  PHOTO_TYPE = 3
  CHECKIN_TYPE = 4
  STATUS_TYPE = 5
  FOLLOW_TYPE = 6
  VIDEO_TYPE = 7
  VIDEO_ALBUM_TYPE = 8
  CORRELATION_TYPE = 9

  def __init__(self, type_id, label):
    self.type_id = type_id
    self.label = label

  def __repr__(self):
    # not including the JSON
    return "<ServiceObjectType('{0},{1}')".format(self.type_id, self.label)


class ServiceEvent(Base):

  ALL_PHOTOS_ID = '_tim_album_all'
  OFME_PHOTOS_ID = '_tim_album_ofme'
  LIKED_PHOTOS_ID = '_tim_album_liked'

  __tablename__ = 'service_event'
  __table_args__ = (UniqueConstraint('author_service_map_id',
                                     'event_id',
                                     name='uidx_service_event_1'),
                    Index('idx_service_event_2', "author_service_map_id", "create_time"),
                    {})

  id = Column(Integer, primary_key=True)

  type_id = Column(Integer,
                   ForeignKey('service_object_type.type_id', ondelete='CASCADE'),
                   nullable=False)
  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)
  service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)

  author_service_map_id = Column(Integer,
                                 ForeignKey('author_service_map.id', ondelete='CASCADE'),
                                 nullable=False)

  event_id = Column(String(255), nullable=False)
  create_time = Column(DateTime, nullable=False)
  modify_time = Column(DateTime, nullable=False)

  correlation_id = Column(String(64), nullable=True)

  url = Column(String(1024))

  headline = Column(String(1024))
  tagline = Column(String(2048))
  caption = Column(String(4096))  # deprecated
  content = Column(String(4096))

  photo_url = Column(String(4096))
  photo_width = Column(Integer)
  photo_height = Column(Integer)
  hidden = Column(Boolean, nullable=False, default=False)

  auxillary_content = Column(Text(65565))  # deprecated

  json = Column(Text(65535))

  def __init__(self,
               author_service_map_id,
               type_id,
               author_id,
               service_id,
               event_id,
               create_time,
               modify_time=None,
               url=None,
               caption=None,
               content=None,
               photo_url=None,
               hidden=False,
               auxillaryContent=None,
               json=None,
               correlation_id=None,
               tagline=None,
               headline=None):
    self.author_service_map_id = author_service_map_id
    self.type_id = type_id
    self.author_id = author_id
    self.service_id = service_id
    self.event_id = event_id
    self.create_time = create_time
    self.modify_time = modify_time if modify_time else create_time
    self.url = url
    self.caption = caption
    self.content = content
    self.photo_url = photo_url
    self.hidden = hidden
    self.auxillary_content = auxillaryContent
    self.json = json
    self.correlation_id = correlation_id
    self.tagline = tagline
    self.headline = headline

  def __repr__(self):
    # not including the JSON
    return "<ServiceEvent('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s')>" % (self.id,
                                                          self.author_service_map_id,
                                                          self.type_id,
                                                          self.author_id,
                                                          self.service_id,
                                                          self.create_time,
                                                          self.url,
                                                          self.caption,
                                                          self.content,
                                                          self.photo_url,
                                                          self.auxillary_content)

  @staticmethod
  def make_well_known_service_event_id(well_known_id, author_id):
    return '{0}@{1}'.format(well_known_id, author_id)


class Relationship(Base):

  __tablename__ = 'relationship'

  parent_author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
  parent_service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), primary_key=True)
  parent_service_event_id = Column(String(255), primary_key=True)

  child_author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
  child_service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), primary_key=True)
  child_service_event_id = Column(String(255), primary_key=True)

  def __init__(self,
               parent_author_id, parent_service_id, parent_service_event_id,
               child_author_id, child_service_id, child_service_event_id):
    self.parent_author_id = parent_author_id
    self.parent_service_id = parent_service_id
    self.parent_service_event_id = parent_service_event_id
    self.child_author_id = child_author_id
    self.child_service_id = child_service_id
    self.child_service_event_id = child_service_event_id

  def __repr__(self):
    # not including the JSON
    return "<Relationship('{0},{1},{2},{3},{4},{5}')".format(self.parent_author_id, self.child_service_id, self.parent_service_event_id,
                                                             self.child_author_id, self.child_service_id, self.child_service_event_id)


class OriginMap(Base):

  __tablename__ = 'origin_map'

  service_name = Column(String(100), nullable=False, primary_key=True)
  origin = Column(String(100), nullable=False, primary_key=True)
  origin_service_name = Column(String(100), nullable=True)

  def __init__(self, serviceName, origin, originServiceName):
    self.service_name = serviceName
    self.origin = origin
    self.origin_service_name = originServiceName

  def __repr__(self):
    return "<OriginMap('%s,%s,%s')>" % (self.service_name, self.origin, self.origin_service_name)


class HighlightType(Base):

  __tablename__ = 'highlight_type'

  id = Column(Integer, primary_key=True)

  label = Column(String(256))

  def __init__(self, label):
    self.label = label

  def __repr__(self):
    return "<HighlightType('%d,%s')>" % (self.id, self.label)


class Highlight(Base):

  __tablename__ = 'highlight'

  id = Column(Integer, primary_key=True)

  highlight_type_id = Column(Integer, ForeignKey('highlight_type.id', ondelete='CASCADE'))

  service_event_id = Column(Integer, ForeignKey('service_event.id', ondelete='CASCADE'))

  weight = Column(Integer)

  caption = Column(String(4096))
  content = Column(String(4096))
  auxillary_content = Column(Text(65565))

  def __init__(self,
               highlightTypeId,
               serviceEventId,
               weight,
               caption=None,
               content=None,
               auxillaryContent=None):
    self.highlight_type_id = highlightTypeId
    self.service_event_id = serviceEventId
    self.weight = weight
    self.caption = caption
    self.content = content
    self.auxillary_content = auxillaryContent

  def __repr__(self):
    return "<Highlight('%d,%d,%d,%d,%s,%s,%s')>" % (self.id,
                                                    self.highlight_type_id,
                                                    self.service_event_id,
                                                    self.weight,
                                                    self.caption,
                                                    self.content,
                                                    self.auxillary_content)


class HighlightServiceEventMap(Base):

  __tablename__ = 'highlight_service_event_map'

  highlight_id = Column(Integer,
                        ForeignKey('highlight.id', ondelete='CASCADE'),
                        nullable=True,
                        primary_key=True)
  service_event_id = Column(Integer,
                            ForeignKey('service_event.id', ondelete='CASCADE'),
                            nullable=True,
                            primary_key=True)

  def __init__(self, highlightId, serviceEventId):
    self.highlight_id = highlightId
    self.service_event_id = serviceEventId

  def __repr__(self):
    return "<HighlightServiceEventMap('%s,%s')>" % (self.highlight_id, self.service_event_id)


class Feature(Base):

  __tablename__ = 'feature'

  id = Column(Integer, primary_key=True)

  name = Column(String(255), unique=True, nullable=False)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "<Feature('%d','%s')>" % (self.id, self.name)

  @classmethod
  def query_by_name(cls, feature_name):
    row = None
    try:
      row = db.Session().query(Feature).filter_by(name=feature_name).one()
    except sqlalchemy.orm.exc.NoResultFound:
      # feature not found
      pass

    return row

  @classmethod
  def exists(cls, feature_name):
    return db.Session().query(Feature).filter(Feature.name == feature_name).count() == 1


class AuthorFeatureMap(Base):

  __tablename__ = 'author_feature_map'

  __table_args__ = (UniqueConstraint('author_id', 'feature_id', name='uidx_author_feature_map_1'),
                    {})

  id = Column(Integer, primary_key=True)

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), nullable=False)
  feature_id = Column(Integer, ForeignKey('feature.id', ondelete='CASCADE'), nullable=False)

  sequence = Column(Integer, nullable=False)

  def __init__(self, authorId, featureId, sequence):
    self.author_id = authorId
    self.feature_id = featureId
    self.sequence = sequence

  def __repr__(self):
    return "<AuthorFeatureMap('%d,%d,%d,%d')>" % (self.id,
                                                  self.author_id,
                                                  self.feature_id,
                                                  self.sequence)


class AuthorFeatureDefault(Base):

  __tablename__ = 'author_feature_default'

  author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
  feature_id = Column(Integer, ForeignKey('feature.id', ondelete='CASCADE'))

  def __init__(self, authorId, featureId):
    self.author_id = authorId
    self.feature_id = featureId

  def __repr__(self):
    return "<AuthorFeatureDefault('%d,%d')>" % (self.author_id, self.feature_id)


class EventScannerPriority(Base):
  __tablename__ = 'event_scanner_priority'

  hash_id = Column(String(64), primary_key=True)
  priority = Column(Integer)
  service_event_id = Column(String(255))
  service_user_id = Column(String(255))
  service_name = Column(String(255))

  @classmethod
  def generate_id(cls, service_event_id, service_user_id, service_name):
    import hashlib
    import base64

    encrypt = hashlib.sha256()
    encrypt.update(service_name + '_' + service_user_id + '_' + service_event_id)
    return base64.urlsafe_b64encode(encrypt.digest())

  def __init__(self, service_event_id, service_user_id, service_name, priority):

    self.priority = priority
    self.service_event_id = service_event_id
    self.service_user_id = service_user_id
    self.service_name = service_name

    self.hash_id = self.generate_id(service_event_id, service_user_id, service_name)

  def __repr__(self):
    return "<EventScannerPriority('{0}', '{1}', '{2}', '{3}')>".format(self.service_event_id,
                                                                       self.service_user_id,
                                                                       self.service_name,
                                                                       self.priority)
