from pyramid.security import Allow
from pyramid.security import Everyone

class RootFactory(object):
  
  __acl__ = [ (Allow, Everyone, 'view'),
              (Allow, 'group:admins', 'admin'),
              (Allow, 'group:authors', 'author') ]

  def __init__(self, request):
    pass
