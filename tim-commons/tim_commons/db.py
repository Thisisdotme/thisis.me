from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

Session = scoped_session(sessionmaker())


def configure_session(url, autocommit=True, echo=False):
  engine = create_engine(url, encoding='utf-8', echo=echo)
  Session.configure(bind=engine, autocommit=autocommit)


class Context:
  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_val, exc_tb):
    Session.flush()
