import sqlalchemy.orm.exc

import tim_commons.db
import mi_schema.models


def query_author_feature(author_id, feature_id):
  query = tim_commons.db.Session().query(mi_schema.models.AuthorFeatureMap)
  query = query.filter_by(author_id=author_id, feature_id=feature_id)

  row = None
  try:
    row = query.one()
  except sqlalchemy.orm.exc.NoResultFound:
    # author feature not found; should be None
    pass

  return row
