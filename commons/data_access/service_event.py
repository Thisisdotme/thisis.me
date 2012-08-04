import logging

import tim_commons.db
import mi_schema.models
import data_access


def query_correlation_event(me_service_id, correlation_id, author_id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(event_id=correlation_id,
                          service_id=me_service_id,
                          author_id=author_id)
  return query.first()


def query_correlated_events(author_id, correlation_id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(author_id=author_id, correlation_id=correlation_id)
  return query.all()


def query_service_event(author_id, service_id, service_event_id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(
      author_id=author_id,
      service_id=service_id,
      event_id=service_event_id)
  return query.first()


def delete(identifier):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(id=identifier)
  count = query.delete()
  logging.info('Deleted %s service events with id: %s', count, identifier)
  return count


def delete_correlation_event(me_service_id, correlation_id, author_id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
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


add_service_event = data_access.add
