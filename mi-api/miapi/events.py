'''
Created on Jan 5, 2012

@author: howard

Request finished callback to automatically call remove on the SQLAlchmey Session object
This keeps bound objects from accumulating and more importantly being stale

'''

from pyramid.events import NewRequest
from pyramid.events import subscriber

#from tim_commons import db


@subscriber(NewRequest)
def request_listener(event):
#  event.request.add_finished_callback(session_remove_callback)
  pass


def session_remove_callback(request):
#  db.Session().remove()
  pass
