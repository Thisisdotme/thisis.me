from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

Session = scoped_session(sessionmaker())


def configure_session(url, autocommit=True, echo=False, pool_recycle=3600):
  engine = create_engine(url, encoding='utf-8', echo=echo, pool_recycle=pool_recycle)
  Session.configure(bind=engine, autocommit=autocommit)


class Context:
  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_val, exc_tb):
    Session.flush()


def configure_mock_session():
  from tim_commons import mock
  global Session
  Session = mock.DummyDBSession


def create_url_from_config(config):
  url = '{protocol}://{user}:{password}@{host}/{database}{encoding}'
  encoding = '?charset=utf8' if bool(config['unicode']) else ''
  return url.format(
      protocol='mysql',
      encoding=encoding,
      **config)
