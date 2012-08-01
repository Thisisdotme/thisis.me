import logging

from tim_commons import db
from mi_schema import models


def query_correlation_event(me_service_id, correlation_id, author_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(event_id=correlation_id,
                          service_id=me_service_id,
                          author_id=author_id)
  return query.first()


def query_correlated_events(author_id, correlation_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(author_id=author_id, correlation_id=correlation_id)
  return query.all()


def query_service_event(author_id, service_id, service_event_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(
      author_id=author_id,
      service_id=service_id,
      event_id=service_event_id)
  return query.first()


def delete(identifier):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(id=identifier)
  count = query.delete()
  logging.info('Deleted %s service events with id: %s', count, identifier)
  return count


def delete_correlation_event(me_service_id, correlation_id, author_id):
  query = db.Session().query(models.ServiceEvent)
  query = query.filter_by(event_id=correlation_id,
                          service_id=me_service_id,
                          author_id=author_id)
  count = query.delete()
  logging.info(
      'Delete %s correlated events with correlation %s and author %s',
      count,
      correlation_id,
      author_id)
  return count
