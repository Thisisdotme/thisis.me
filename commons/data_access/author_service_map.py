from tim_commons import db
from mi_schema import models


def query_asm_by_author_and_service(author_id, service_id):
  query = db.Session().query(models.AuthorServiceMap)
  query = query.filter_by(author_id=author_id,
                          service_id=service_id)
  return query.one()
