import logging

from tim_commons import db
from mi_schema import models


def delete(identifier):
  query = db.Session().query(models.EventScannerPriority)
  query = query.filter_by(hash_id=identifier)
  count = query.delete()
  logging.info('Delete %s rows with id: %s', count, identifier)
  return count
