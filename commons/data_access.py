from tim_commons import db
from mi_schema import models


def query_correlation_event(me_service_id, correlation_id, author_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(event_id=correlation_id,
                          service_id=me_service_id,
                          author_id=author_id)
  return query.first()


def query_asm(author_id, service_id):
  query = db.Session().query(models.AuthorServiceMap)
  query = query.filter_by(author_id=author_id,
                          service_id=service_id)
  return query.one()


def query_correlated_events(author_id, correlation_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(author_id=author_id, correlation_id=correlation_id)
  return query.all()


def query_author(author_id):
  return db.Session().query(models.Author).get(author_id)
