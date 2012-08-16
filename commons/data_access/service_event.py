import logging

import sqlalchemy.orm.exc

import tim_commons.db
import mi_schema.models
import data_access.post_type


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


def query_photo_album(author_id, id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(
      id=id,
      author_id=author_id,
      type_id=data_access.post_type.label_to_id('photo_album'))

  row = None
  try:
    row = query.one()
  except sqlalchemy.orm.exc.NoResultFound:
    # event not found variable should be None
    pass

  return row


def query_photos_page(
    author_id,
    album_event_id,
    album_service_id,
    limit,
    since_date=None,
    since_service_id=None,
    since_event_id=None,
    until_date=None,
    until_service_id=None,
    until_event_id=None):
  all_album_event_id = mi_schema.models.ServiceEvent.make_well_known_service_event_id(
      mi_schema.models.ServiceEvent.ALL_PHOTOS_ID,
      author_id)

  if (album_event_id == all_album_event_id and
      album_service_id == data_access.service.name_to_id('me')):
    # query the all photo album
    query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
    query = query.filter_by(
        author_id=author_id,
        type_id=data_access.post_type.label_to_id('photo'))
    query = query.order_by(
        mi_schema.models.ServiceEvent.create_time.desc(),
        mi_schema.models.ServiceEvent.service_id.desc(),
        mi_schema.models.ServiceEvent.event_id.desc())
  else:
    # query a specific album
    query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
    query = query.join(
        mi_schema.models.Relationship,
        sqlalchemy.and_(
          mi_schema.models.Relationship.child_author_id ==
            mi_schema.models.ServiceEvent.author_id,
          mi_schema.models.Relationship.child_service_id ==
            mi_schema.models.ServiceEvent.service_id,
          mi_schema.models.Relationship.child_service_event_id ==
            mi_schema.models.ServiceEvent.event_id))
    query = query.filter(
        sqlalchemy.and_(
          mi_schema.models.Relationship.parent_author_id == author_id,
          mi_schema.models.Relationship.parent_service_id == album_service_id,
          mi_schema.models.Relationship.parent_service_event_id == album_event_id))
    query = query.order_by(
        mi_schema.models.ServiceEvent.create_time.desc(),
        mi_schema.models.ServiceEvent.service_id.desc(),
        mi_schema.models.ServiceEvent.event_id.desc())

  # paging check point
  if since_date:
    query = query.filter(mi_schema.models.ServiceEvent.create_time >= since_date)
  if since_service_id:
    query = query.filter(mi_schema.models.ServiceEvent.service_id >= since_service_id)
  if since_event_id:
    query = query.filter(mi_schema.models.ServiceEvent.event_id > since_event_id)
  if until_date:
    query = query.filter(mi_schema.models.ServiceEvent.create_time <= until_date)
  if until_service_id:
    query = query.filter(mi_schema.models.ServiceEvent.service_id <= until_service_id)
  if until_event_id:
    query = query.filter(mi_schema.models.ServiceEvent.event_id < until_event_id)

  return query.limit(limit)


def query_service_event_by_id(author_id, id):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(
      author_id=author_id,
      id=id)

  row = None
  try:
    row = query.one()
  except sqlalchemy.orm.exc.NoResultFound:
    # event not found variable should be None
    pass

  return row


def query_service_events_page(
    author_id,
    limit,
    since_date=None,
    since_service_id=None,
    since_event_id=None,
    until_date=None,
    until_service_id=None,
    until_event_id=None):
  query = tim_commons.db.Session().query(mi_schema.models.ServiceEvent)
  query = query.filter_by(author_id=author_id)

  # don't show photo albums from me and instagram
  me_id = data_access.service.name_to_id('me')
  instagram_id = data_access.service.name_to_id('instagram')
  query = query.filter(sqlalchemy.or_(
        mi_schema.models.ServiceEvent.type_id != data_access.post_type.label_to_id('photo_album'),
        sqlalchemy.and_(mi_schema.models.ServiceEvent.service_id != me_id,
                        mi_schema.models.ServiceEvent.service_id != instagram_id)))

  if since_date:
    query = query.filter(mi_schema.models.ServiceEvent.create_time >= since_date)
  if since_service_id:
    query = query.filter(mi_schema.models.ServiceEvent.service_id >= since_service_id)
  if since_event_id:
    query = query.filter(mi_schema.models.ServiceEvent.event_id > since_event_id)
  if until_date:
    query = query.filter(mi_schema.models.ServiceEvent.create_time <= until_date)
  if until_service_id:
    query = query.filter(mi_schema.models.ServiceEvent.service_id <= until_service_id)
  if until_event_id:
    query = query.filter(mi_schema.models.ServiceEvent.event_id < until_event_id)

  query = query.order_by(
      mi_schema.models.ServiceEvent.create_time.desc(),
      mi_schema.models.ServiceEvent.service_id.desc(),
      mi_schema.models.ServiceEvent.event_id.desc())

  return query.limit(limit)


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
