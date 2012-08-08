import sqlalchemy.orm.exc

import tim_commons.db
import mi_schema.models
import data_access


def query_asm_by_author_and_service(author_id, service_id):
  query = tim_commons.db.Session().query(mi_schema.models.AuthorServiceMap)
  query = query.filter_by(author_id=author_id,
                          service_id=service_id)
  row = None
  try:
    row = query.one()
  except sqlalchemy.orm.exc.NoResultFound:
    # asm not found varaible should be None
    pass

  return row


add_author_service_map = data_access.add
