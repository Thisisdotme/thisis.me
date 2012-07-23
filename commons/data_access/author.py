from tim_commons import db
from mi_schema import models


def query_author(author_id):
  return db.Session().query(models.Author).get(author_id)
