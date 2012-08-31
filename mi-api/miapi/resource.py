import pyramid.security

import data_access.author
import mi_schema.models


class Root:
  def __init__(self, request):
    self.request = request

  def __getitem__(self, key):
    if key == 'v1':
      return location_aware(V1Root(), self, key)

    raise KeyError('key "{key}" not a valid root entry'.format(key=key))


class V1Root:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'login'),
      (pyramid.security.Allow, pyramid.security.Authenticated, 'logout'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    resource = None
    if key == 'authors':
      resource = Authors()
    elif key == 'services':
      resource = Services()
    elif key == 'features':
      resource = Features
    elif key == 'reservations':
      resource = Reservations()
    elif key == 'status':
      resource = Status()
    elif key == 'self':
      author_id = pyramid.security.unauthenticated_userid(self.request)
      if author_id is None:
        raise KeyError('Key "{key}" not valid because user is not authenticated'.format(key=key))

      author = data_access.author.query_author(author_id)
      if author is None:
        raise KeyError('Author id "{0}" is not an existing author'.format(author_id))

      resource = Author(author)

    if resource is None:
      raise KeyError('Key "{key}" not a valid v1 root entry'.format(key=key))

    return location_aware(resource, self, key)

  @property
  def request(self):
    return self.__parent__.request


class Status:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      pyramid.security.DENY_ALL]


class Reservations:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'create'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    return location_aware(Reservation(key), self, key)


class Reservation:
  def __init__(self, author_name):
    self.author_name = author_name


class Authors:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'create'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    try:
      author = data_access.author.query_author(int(key))
    except ValueError:
      # Key is not an integer assume that it is an author_name
      # TODO: we can remove this once the client changes to using id.
      author = data_access.author.query_by_author_name(key)

    if author is None:
      raise KeyError('key "{key}" is not an existing author'.format(key=key))

    return location_aware(Author(author), self, author.id)


class Author:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
        (pyramid.security.Allow, self.author.id, 'write'),
        (pyramid.security.Allow, self.author.id, 'create'),
        pyramid.security.DENY_ALL]

  def __init__(self, author):
    self.author = author

  def __getitem__(self, key):
    resource = None
    if key == 'profile':
      pass  # TODO: implement this
    elif key == 'highlights':
      pass  # TODO: implement this
    elif key == 'events':
      resource = Events()
    elif key == 'services':
      resource = AuthorServices()
    elif key == 'photoalbums':
      resource = PhotoAlbums()
    elif key == 'features':
      resource = AuthorFeatures()
    elif key == 'groups':
      resource = AuthorGroups()

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('Key "{key}" not a valid author entry'.format(key=key))


class AuthorFeatures:
  @property
  def author(self):
    return self.__parent__.author

  def __getitem__(self, key):
    if key == 'default':
      raise KeyError('Key "{key}" not a valid author feature entry'.format(key=key))

    feature = mi_schema.models.Feature.query_by_name(key)

    if feature is None:
      raise KeyError('Feature ({feature}) does not exist'.format(feature=key))

    author_feature = data_access.author_feature_map.query_author_feature(
        self.author.id,
        feature.id)

    if author_feature is None:
      raise KeyError('Author feature ({author}, {feature}) does not exist'.format(
        author=self.author.id,
        feature=feature.feature_id))

    return location_aware(AuthorFeature(feature, author_feature), self, key)


class AuthorFeature:
  def __init__(self, feature, author_feature):
    self.author_feature = author_feature
    self.feature = feature

  @property
  def author(self):
    return self.__parent__.author


class AuthorServices:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
        (pyramid.security.Allow, self.author.id, ['write', 'create']),
        pyramid.security.DENY_ALL]

  @property
  def author(self):
    return self.__parent__.author

  def __getitem__(self, key):
    service = data_access.service.name_to_service.get(key)
    if service is None:
      raise KeyError('Service ({service}) does not exist'.format(service=key))

    asm = data_access.author_service_map.query_asm_by_author_and_service(
        self.author.id,
        service.id)
    if asm is None:
      raise KeyError('Author service ({author}, {service}) does not exist'.format(
        author=self.author.id,
        service=service.id))

    return location_aware(AuthorService(asm, key), self, key)


class AuthorService:
  def __init__(self, author_service_map, service_name):
    self.author_service_map = author_service_map
    self.service_name = service_name

  @property
  def author(self):
    return self.__parent__.author


# This is currently not used. It is suppose to cover the case where we want to page photoalbum
# and display all photos, photos of me, photos liked.
class MetaPhotoAlbums():
  def __getitem__(self, key):
    try:
      album = data_access.service_event.query_meta_photo_album(self.author.id, int(key))
    except ValueError:
      raise KeyError('key "{key}" not a valid photo albums entry'.format(key=key))

    if album is None:
      raise KeyError('Meta photo album ({author}, {album}) does not exist'.format(
            author=self.author.id,
            album=key))

    return location_aware(PhotoAlbum(album), self, album.id)

  @property
  def author(self):
    return self.__parent__.author


class PhotoAlbums:
  def __getitem__(self, key):
    try:
      album = data_access.service_event.query_photo_album(self.author.id, int(key))
    except ValueError:
      raise KeyError('key "{key}" not a valid photo albums entry'.format(key=key))

    if album is None:
      raise KeyError('Photo album ({author}, {album}) does not exist'.format(
            author=self.author.id,
            album=key))

    return location_aware(PhotoAlbum(album), self, album.id)

  @property
  def author(self):
    return self.__parent__.author


class PhotoAlbum:
  def __init__(self, album):
    self.album = album
    self.album_id = album.id

  def __getitem__(self, key):
    if key == 'photos':
      resource = Photos()

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('key "{key}" not a valid photo album entry.'.format(key=key))

  @property
  def author(self):
    return self.__parent__.author


class Photos:
  @property
  def author(self):
    return self.__parent__.author

  @property
  def album_id(self):
    return self.__parent__.album_id

  @property
  def album(self):
    return self.__parent__.album


class Events:
  def __getitem__(self, key):
    try:
      event = data_access.service_event.query_service_event_by_id(self.author.id, int(key))
    except ValueError:
      raise KeyError('key "{key}" not a valid event id'.format(key=key))

    if event is None:
      raise KeyError('Event ({author}, {event}) does not exist.'.format(
            author=self.author.id,
            event=key))

    return location_aware(Event(event), self, event.id)

  @property
  def author(self):
    return self.__parent__.author


class Event:
  def __init__(self, event):
    self.event = event
    self.event_id = event.id

  @property
  def author(self):
    return self.__parent__.author


class Services:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'write'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'create'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    if not mi_schema.models.Service.exists(key):
      raise KeyError('key "{key}" not a valid Services entry'.format(key=key))

    return location_aware(Service(key), self, key)


class Service:
  def __init__(self, service_name):
    self.name = service_name


class Features:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'write'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'create'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    feature = mi_schema.models.Feature.query_by_name(key)
    if not feature:
      raise KeyError('key "{key}" not a valid Features entry'.format(key=key))

    return location_aware(Feature(feature), self, key)


class Feature:
  def __init__(self, feature):
    self._feature = feature

  @property
  def feature(self):
    return self._feature

  @property
  def name(self):
    return self._feature.name


class AuthorGroups:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, self.author.id, 'read'),
        (pyramid.security.Allow, self.author.id, 'write'),
        (pyramid.security.Allow, self.author.id, 'create'),
        pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    group_name = key
    author_group = mi_schema.models.AuthorGroup.lookup(self.author.id, group_name)
    if not author_group:
      raise KeyError('key "{key}" not a valid Group entry'.format(key=group_name))

    return location_aware(AuthorGroup(author_group), self, group_name)

  @property
  def author(self):
    return self.__parent__.author


class AuthorGroup:
  def __init__(self, author_group):
    self._author_group = author_group

  def __getitem__(self, key):
    resource = None
    if key == 'members':
      resource = AuthorGroupMembers()
    elif key == 'highlights':
      resource = AuthorGroupHighlights()
    elif key == 'events':
      resource = AuthorGroupEvents()

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('Key "{key}" not a valid groups entry'.format(key=key))

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_group(self):
    return self._author_group


class AuthorGroupMembers:
  def __getitem__(self, key):
    member = key
    author_group_member = mi_schema.models.AuthorGroupMap.lookup(
        self.author.id,
        self.author_group.group_name,
        member)
    if not author_group_member:
      raise KeyError('key "{key}" not a valid member entry'.format(key=member))

    return location_aware(AuthorGroupMember(author_group_member), self, key)

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_group(self):
    return self.__parent__.author_group


class AuthorGroupMember:
  def __init__(self, member):
    self._member = member

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_group(self):
    return self.__parent__.author_group

  @property
  def author_group_member(self):
    return self._member


class AuthorGroupHighlights:
  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_group(self):
    return self.__parent__.author_group


class AuthorGroupEvents:
  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_group(self):
    return self.__parent__.author_group


def location_aware(resource, parent, name):
  resource.__parent__ = parent
  resource.__name__ = name
  return resource


def root_factory(request):
  return location_aware(Root(request), None, '')
