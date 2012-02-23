import urllib2

'''
Created on Dec 12, 2011

@author: howard
'''

class RequestWithMethod(urllib2.Request):

  """Workaround for using PUT, DELETE, and HEAD with urllib2"""
  def __init__(self, url, method, data=None, headers={}, origin_req_host=None, unverifiable=False):
    self._method = method
    urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
  
  def get_method(self):
    if self._method:
      return self._method
    else:
      return urllib2.Request.get_method(self)
