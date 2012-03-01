from sqlalchemy.orm import join

from mi_schema.models import Author
from mi_schema.models import AccessGroup
from mi_schema.models import AuthorAccessGroupMap

from globals import DBSession

# get the groups the user is a member of
#
def groupfinder(authorname, request):

  dbsession = DBSession()
  
  author = dbsession.query(Author).filter_by(author_name=authorname).first()
  
  # TODO: add handling for invalid author name
  if author is not None:
    groups = dbsession.query(AccessGroup).select_from(join(AuthorAccessGroupMap, AccessGroup, AuthorAccessGroupMap.group_id==AccessGroup.id)).filter(AuthorAccessGroupMap.author_id==author.id).all()
    return [group.group_name for group in groups]
  
  return []
  