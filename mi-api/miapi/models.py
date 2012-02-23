
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import mi_schema.models as mi_schema

DBSession = scoped_session(sessionmaker())
SimpleDBSession = sessionmaker()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    mi_schema.Base.metadata.bind = engine
    mi_schema.Base.metadata.create_all(engine)
