import sqlalchemy.orm.exc

import tim_commons.db
import mi_schema.models
import data_access


def query_author(author_id):
  return tim_commons.db.Session().query(mi_schema.models.Author).get(author_id)


def query_by_author_name(author_name):
  query = tim_commons.db.Session().query(mi_schema.models.Author)
  query = query.filter_by(author_name=author_name)

  author = None
  try:
    author = query.one()
  except sqlalchemy.orm.exc.NoResultFound:
    # author not found varaible should be None
    pass

  return author


def query_authors():
  return tim_commons.db.Session().query(mi_schema.models.Author).all()


add_author = data_access.add
delete_author = data_access.delete
