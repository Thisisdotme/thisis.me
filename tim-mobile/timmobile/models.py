
import mi_schema.models as mi_schema

from globals import DBSession

def initialize_sql(engine):
  DBSession.configure(bind=engine)
  mi_schema.Base.metadata.bind = engine
