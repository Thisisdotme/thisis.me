class Root:
  def __init__(self):
    self.v1_root = location_aware(V1Root(), self, 'v1')

  def __getitem__(self, key):
    if key == self.v1_root.__name__:
      return self.v1_root

    raise KeyError('key "{key}" not a valid root entry'.format(key=key))


class V1Root:
  def __init__(self):
    self.authors = location_aware(Authors(), self, 'authors')

    self.services = location_aware(Services(), self, 'services')

    self.features = location_aware(Features(), self, 'features')

  def __getitem__(self, key):
    if key == self.authors.__name__:
      return self.authors
    elif key == self.services.__name__:
      return self.services
    elif key == self.features.__name__:
      return self.features

    raise KeyError('key "{key}" not a valid v1 root entry'.format(key=key))


class Authors:
  def __getitem__(self, author_name):
    return location_aware(Author(author_name), self, author_name)


class Author:
  def __init__(self, author_name):
    self.author_name = author_name

  def __getitem__(self, key):
    resource = None
    if key == 'profile':
      pass  # TODO: implement this
    elif key == 'highlights':
      pass  # TODO: implement this
    elif key == 'events':
      resource = Events()
    elif key == 'topstories':
      pass  # TODO: implement this
    elif key == 'services':
      pass  # TODO: implement this
    elif key == 'photoaulbums':
      pass  # TODO implement this
    elif key == 'features':
      pass  # TODO implement this

    if resource:
      return location_aware(resource, self, key)

    raise KeyError('Key "{key}" not a valid author entry'.format(key=key))


class Events:
  def __getitem__(self, event_id):
    return location_aware(Event(event_id), self, event_id)


class Event:
  def __init__(self, event_id):
    self.event_id = event_id


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


_root = Root()
