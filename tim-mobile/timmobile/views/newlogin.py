'''
Created on Feb 23, 2012

@author: howard
'''
from mi_schema.models import Author
from mi_url.RequestWithMethod import RequestWithMethod
from pprint import PrettyPrinter
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import authenticated_userid, remember, forget
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy import func
from timmobile.globals import DBSession
from urllib2 import HTTPError
import json
import logging
import urllib2

log = logging.getLogger(__name__)

@view_config(route_name='newlogin', renderer='timmobile:templates/newlogin.pt')
def newuser(request):
  fullname = ''
  email = ''
  login = ''
  password = ''
  message = ''
  
  forward = request.params.get('forward') or request.route_url('accounts')

  if 'form.submitted' in request.POST:
    login = request.POST.get('newlogin', '')
    password = request.POST.get('newpassword', '')
    fullname = request.POST.get('fullname', '')
    email = request.POST.get('email', '')

    # query the db to check username availability
    dbsession = DBSession()
    count = dbsession.query(func.count('*')).select_from(Author).filter_by(author_name=login).scalar()
    count += dbsession.query(func.count('*')).select_from(Author).filter_by(email=email).scalar()
    
    if count <= 0:
      log.info('Creating user: %s' % login)
      try:
        json_payload = json.dumps(dict(password=password, fullname=fullname, email=email))
        headers = {'Content-Type':'application/json; charset=utf-8'}
        req = RequestWithMethod('%s/v1/authors/%s' % (request.registry.settings['mi.api.endpoint'],login),
                                'PUT',
                                json_payload,
                                headers)
        res = urllib2.urlopen(req)
        resJSON = json.loads(res.read())
        request.session['logged_id'] = '1'
        headers = remember(request, login)
        return HTTPFound(location=forward, headers=headers)
      except HTTPError, e:
        msg = json.load(e);
        message = 'Error: ' + str(e.code) + ': ' + e.msg + ': ' + msg['error']
    else:
      message = 'Email/Login already taken'
      
  return dict(
              message = message,
              url = request.route_path('newlogin'),
              forward = forward,
              fullname = fullname,
              email = email,
              login = login,
              password = password,
              title = 'Create Login',
              api_endpoint = request.registry.settings['mi.api.endpoint'],
              author_name = ''
              )
