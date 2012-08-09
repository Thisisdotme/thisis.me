import pyramid.security

import data_access.author

import mi_schema.models


class Root:
  def __init__(self):
    self.v1_root = location_aware(V1Root(), self, 'v1')

  def __getitem__(self, key):
    if key == self.v1_root.__name__:
      return self.v1_root

    raise KeyError('key "{key}" not a valid root entry'.format(key=key))


class V1Root:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'login'),
      (pyramid.security.Allow, pyramid.security.Authenticated, 'logout'),
      pyramid.security.DENY_ALL]

  def __init__(self):
    self.authors = location_aware(Authors(), self, 'authors')
    self.services = location_aware(Services(), self, 'services')
    self.features = location_aware(Features(), self, 'features')
    self.reservations = location_aware(Reservations(), self, 'reservations')

  def __getitem__(self, key):
    if key == self.authors.__name__:
      return self.authors
    elif key == self.services.__name__:
      return self.services
    elif key == self.features.__name__:
      return self.features
    elif key == self.reservations.__name__:
      return self.reservations

    raise KeyError('key "{key}" not a valid v1 root entry'.format(key=key))


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
      author_id = int(key)
      author = data_access.author.query_author(author_id)
    except ValueError:
      # Key is not an integer assume that it is an author_name
      # TODO: we can remove this once the client changes to using id.
      author = data_access.author.query_by_author_name(key)

    if not author:
      raise KeyError('key "{key}" not a valid Authors entry'.format(key=key))

    return location_aware(Author(author), self, author.id)


class Author:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
        (pyramid.security.Allow, self.author_id, 'write'),
        (pyramid.security.Allow, self.author_id, 'create'),
        pyramid.security.DENY_ALL]

  def __init__(self, author):
    self._author = author
    self.author_id = author.id

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

  @property
  def author(self):
    return self._author


class AuthorFeatures:
  @property
  def author_id(self):
    return self.__parent__.author_id

  def __getitem__(self, key):
    if key == 'default':
      raise KeyError('Key "{key}" not a valid author feature entry'.format(key=key))

    return location_aware(AuthorFeature(key), self, key)


class AuthorFeature:
  def __init__(self, feature_name):
    self.feature_name = feature_name

  @property
  def author_id(self):
    return self.__parent__.author_id


class AuthorServices:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, self.author_id, ['read', 'write', 'create']),
        pyramid.security.DENY_ALL]

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id

  def __getitem__(self, key):
    return location_aware(AuthorService(key), self, key)


class AuthorService:
  def __init__(self, service_name):
    self.service_name = service_name

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


class PhotoAlbums:
  def __getitem__(self, key):
    try:
      album_id = int(key)
    except ValueError:
      raise KeyError('key "{key}" not a valid photo albums entry'.format(key=key))

    return location_aware(PhotoAlbum(album_id), self, key)

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


class PhotoAlbum:
  def __init__(self, album_id):
    self.album_id = album_id

  def __getitem__(self, key):
    if key == 'photos':
      resource = Photos()

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('key "{key}" not a valid photo album entry.'.format(key=key))

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


class Photos:
  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id

  @property
  def album_id(self):
    return self.__parent__.album_id


class Events:
  def __getitem__(self, key):
    try:
      event_id = int(key)
    except ValueError:
      raise KeyError('key "{key}" not a valid Authors entry'.format(key=key))

    return location_aware(Event(event_id), self, event_id)

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


class Event:
  def __init__(self, event_id):
    self.event_id = event_id

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


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
    self._name = service_name

  @property
  def name(self):
    return self._name


class Features:
  __acl__ = [
      (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'write'),
      (pyramid.security.Allow, pyramid.security.Everyone, 'create'),
      pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    if not mi_schema.models.Feature.exists(key):
      raise KeyError('key "{key}" not a valid Features entry'.format(key=key))

    return location_aware(Feature(key), self, key)


class Feature:
  def __init__(self, feature_name):
    self._name = feature_name

  @property
  def name(self):
    return self._name


class AuthorGroups:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, self.author_id, 'read'),
        (pyramid.security.Allow, self.author_id, 'write'),
        (pyramid.security.Allow, self.author_id, 'create'),
        pyramid.security.DENY_ALL]

  def __getitem__(self, key):
    group_name = key
    author_group = mi_schema.models.AuthorGroup.lookup(self.author_id, group_name)
    if not author_group:
      raise KeyError('key "{key}" not a valid Group entry'.format(key=group_name))

    return location_aware(AuthorGroup(author_group), self, group_name)

  @property
  def author(self):
    return self.__parent__.author

  @property
  def author_id(self):
    return self.__parent__.author_id


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
    author_group_member = mi_schema.models.AuthorGroupMap.lookup(self.author.id, self.author_group.group_name, member)
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
  return _root


_root = location_aware(Root(), None, '')
