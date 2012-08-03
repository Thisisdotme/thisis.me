from tim_commons import db
from mi_schema import models


def query_author(author_id):
  return db.Session().query(models.Author).get(author_id)


def query_by_author_name(author_name):
  return db.Session().query(models.Author).filter_by(author_name=author_name).one()
