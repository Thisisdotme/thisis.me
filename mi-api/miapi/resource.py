import pyramid.security

import data_access.author


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
    except ValueError:
      # Key is not an integer assume that it is an author_name
      # TODO: we can remove this once the client changes to using id.
      author = data_access.author.query_by_author_name(key)
      if author:
        author_id = author.id
      else:
        raise KeyError('key "{key}" not a valid Authors entry'.format(key=key))

    return location_aware(Author(author_id), self, author_id)


class Author:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, pyramid.security.Everyone, 'read'),
        (pyramid.security.Allow, self.author_id, 'write'),
        pyramid.security.DENY_ALL]

  def __init__(self, author_id):
    self.author_id = author_id

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
      pass  # TODO implement this

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('Key "{key}" not a valid author entry'.format(key=key))


class AuthorServices:
  @property
  def __acl__(self):
    return [
        (pyramid.security.Allow, self.author_id, 'read'),
        (pyramid.security.Allow, self.author_id, 'write'),
        pyramid.security.DENY_ALL]

  @property
  def author_id(self):
    return self.__parent__.author_id

  def __getitem__(self, key):
    return location_aware(AuthorService(key), self, key)


class AuthorService:
  def __init__(self, service_name):
    self.service_name = service_name

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
  def author_id(self):
    return self.__parent__.author_id


class Photos:
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
  def author_id(self):
    return self.__parent__.author_id


class Event:
  def __init__(self, event_id):
    self.event_id = event_id

  @property
  def author_id(self):
    return self.__parent__.__parent__.author_id


class Services:
  # TODO: implement this
  pass


class Features:
  # TODO: implement this
  pass


def location_aware(resource, parent, name):
  resource.__parent__ = parent
  resource.__name__ = name
  return resource


def root_factory(request):
  return _root


_root = location_aware(Root(), None, '')
