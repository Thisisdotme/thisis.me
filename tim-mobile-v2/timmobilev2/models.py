
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

DBSessionXX = scoped_session(sessionmaker())
BaseXX = declarative_base()
