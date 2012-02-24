'''
Created on Jan 6, 2012

@author: howard
'''

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

DBSession = scoped_session(sessionmaker())


