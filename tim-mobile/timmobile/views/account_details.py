'''
Created on Feb 23, 2012

@author: howard
'''
from tim_commons.request_with_method import RequestWithMethod
from pyramid.view import view_config
import json
import urllib2
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='account_details', request_method='GET', permission='author', renderer='timmobile:templates/account_details.pt')
def getAccount(request):
  featureName = request.matchdict['featurename']

  message = ''
  messages = request.session.pop_flash()
  if len(messages) > 0:
    message = messages[0]

  return { 'feature': featureName,
           'api_endpoint':request.registry.settings['mi.api.endpoint'],
           'url': request.route_url('account_details', featurename=featureName),
           'message':message }

@view_config(route_name='account_details', request_method='POST', permission='author', renderer='timmobile:templates/account_details.pt')
def postAccount(request):
  featureName = request.matchdict['featurename']
  req = RequestWithMethod('%s/v1/authors/%s/services/%s' %
                          (request.registry.settings['mi.api.endpoint'], authenticated_userid(request), featureName), 
                          'DELETE')
  res = urllib2.urlopen(req)
  resJSON = json.loads(res.read())
  
  
  if featureName == 'googleplus':
    del(request.session['googlePlus_access_token'], request.session['googlePlus_user_id'])
  elif featureName == 'facebook':
    del(request.session['facebook_access_token'], request.session['facebook_user_id'])
  elif featureName == 'flickr':
    del(request.session['flickr_access_token'])
  elif featureName == 'foursquare':
    del(request.session['foursquare_access_token'], request.session['foursquare_user_id'])
  elif featureName == 'instagram':
    del(request.session['instagram_access_token'])
  elif featureName == 'linkedin':
    del(request.session['linkedin_access_token'], request.session['linkedin_access_token_secret'])
  elif featureName == 'twitter':
    del(request.session['twitter_access_token'], request.session['twitter_access_token_secret'])
  else:
    print("No account cleanup set up for feature: " + featureName)
     
  return HTTPFound(request.route_url('accounts'))
