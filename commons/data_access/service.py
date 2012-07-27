from tim_commons import db
from mi_schema import models

name_to_service = {}
id_to_service = {}


def name_to_id(name):
  return name_to_service[name].id


def initialize():
  services = query_all_services()

  for service in services:
    db.Session().expunge(service)
    name_to_service[service.service_name] = service
    id_to_service[service.id] = service


def query_all_services():
  query = db.Session().query(models.Service)
  return query.all()


def mock_initialize():
  for identifier, name in [(1, 'me'), (2, 'facebook'), (3, 'instagram')]:
    service = models.Service(name, '', '', '', '', '', '')
    service.id = identifier

    name_to_service[name] = service
    id_to_service[identifier] = service
