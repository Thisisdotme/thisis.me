'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from miapi.models import DBSession

from mi_schema.models import Author, AuthorGroup, AuthorGroupMap

from miapi.globals import DEFAULT_AUTHOR_GROUP

log = logging.getLogger(__name__)

class AuthorGroupBasics(object):
  '''
  classdocs
  '''
  
  '''
  class variables
  '''
  
  '''
  Constructor
  '''
  def __init__(self, request):
    self.request = request
    self.dbSession = DBSession()


  # GET /v1/authors/{authorname}/groups
  #
  # return all authors that match the specified search criteria
  #
  @view_config(route_name='author.groups', request_method='GET', renderer='jsonp', http_cache=0)
  def listGroupsHndlr(self):

    authorName = self.request.matchdict['authorname']

    try:
      authorId, = self.dbSession.query(Author.id).filter(Author.author_name==authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    groupList = []
    for group in self.dbSession.query(AuthorGroup).filter(AuthorGroup.author_id==authorId).order_by(AuthorGroup.group_name):
      groupList.append(group.toJSONObject())

    return {'author_id': authorId, 'groups': groupList}


  # GET /v1/authors/{authorname}/groups/{groupname}
  #
  @view_config(route_name='author.groups.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getGroupDetailHndlr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    return authorGroup.toJSONObject()



  # PUT /v1/authors/{authorname}/groups/{groupname}
  #
  @view_config(route_name='author.groups.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def addUpdateGroupHndlr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']

    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    authorGroup = AuthorGroup(authorId,groupName)
    jsonObject = None

    try:
      self.dbSession.add(authorGroup)
      self.dbSession.flush()
      jsonObject = authorGroup.toJSONObject()
      self.dbSession.commit()
      log.info("created author_group: %s" % authorGroup)
  
    except IntegrityError, e:
      self.dbSession.rollback()
      self.request.response.status_int = 409
      return {'error':e.message}
    
    return jsonObject



  # DELETE /v1/authors/{authorname}/groups/{groupname}
  #
  @view_config(route_name='author.groups.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteGroupHndlr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
  
    if groupName == DEFAULT_AUTHOR_GROUP:
      self.request.response.status_int = 403
      return {'error':'cannot delete the required group %s' % groupName}
     
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    self.dbSession.delete(authorGroup)
    
    self.dbSession.commit()  
  
    return authorGroup.toJSONObject()

  
  # GET /v1/authors/{authorname}/groups/{groupname}/members
  #
  @view_config(route_name='author.groups.members', request_method='GET', renderer='jsonp', http_cache=0)
  def getGroupMembersHndr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']

    try:
      authorId, = self.dbSession.query(Author.id).filter(Author.author_name==authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroup = self.dbSession.query(AuthorGroup).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    memberList = []
    for member in self.dbSession.query(Author).join(AuthorGroupMap).filter(Author.id==AuthorGroupMap.author_id).filter(AuthorGroupMap.author_group_id==authorGroup.id).order_by(Author.author_name):
      memberList.append(member.toJSONObject())

    responseJSON = authorGroup.toJSONObject();
    responseJSON['author_name'] = authorName
    responseJSON['members'] = memberList
    
    return responseJSON


  # GET /v1/authors/{authorname}/groups/{groupname}/members/{member}
  #
  @view_config(route_name='author.groups.members.CRUD', request_method='GET', renderer='jsonp', http_cache=0)
  def getGroupMemberHndlr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
    memberName = self.request.matchdict['member']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroupId, = self.dbSession.query(AuthorGroup.id).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    try:
      member = self.dbSession.query(Author).filter_by(author_name=memberName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown member author %s' % authorName}

    try:
      mapping = self.dbSession.query(AuthorGroupMap).filter(and_(AuthorGroupMap.author_group_id==authorGroupId,AuthorGroupMap.author_id==member.id)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown member %s in group %s for author %s' % (memberName,groupName,authorName)}

    responseJSON = mapping.toJSONObject()
    responseJSON['author_id'] = authorId
    responseJSON['author_name'] = authorName
    responseJSON['group_name'] = groupName
    responseJSON['member'] = member.toJSONObject()

    return responseJSON


  # PUT /v1/authors/{authorname}/groups/{groupname}/members/{member}
  #  
  @view_config(route_name='author.groups.members.CRUD', request_method='PUT', renderer='jsonp', http_cache=0)
  def addUpdateGroupMemberHndlr(self):
    
    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
    memberName = self.request.matchdict['member']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroupId, = self.dbSession.query(AuthorGroup.id).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    try:
      member = self.dbSession.query(Author).filter_by(author_name=memberName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown member author %s' % memberName}

    mapping = AuthorGroupMap(authorGroupId,member.id)

    try:
      self.dbSession.add(mapping)
      self.dbSession.flush()
      self.dbSession.commit()
      log.info("Added %s to %s's author_group %s" % (memberName,authorName,groupName))
  
    except IntegrityError, e:
      self.dbSession.rollback()
      self.request.response.status_int = 409
      return {'error':e.message}
    
    return {'author_name': authorName,
            'author_id': authorId,
            'group' : 
              { 'group_name': groupName,
                'author_group_id': authorGroupId,
                'member': member.toJSONObject() 
              }
            }


  # DELETE /v1/authors/{authorname}/groups/{groupname}/members/{member}
  #
  @view_config(route_name='author.groups.members.CRUD', request_method='DELETE', renderer='jsonp', http_cache=0)
  def deleteGroupMemberHndlr(self):

    authorName = self.request.matchdict['authorname']
    groupName = self.request.matchdict['groupname']
    memberName = self.request.matchdict['member']
  
    try:
      authorId, = self.dbSession.query(Author.id).filter_by(author_name=authorName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown author %s' % authorName}

    try:
      authorGroupId, = self.dbSession.query(AuthorGroup.id).filter(and_(AuthorGroup.author_id==authorId,AuthorGroup.group_name==groupName)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown group %s for author %s' % (groupName,authorName)}

    try:
      memberId, = self.dbSession.query(Author.id).filter_by(author_name=memberName).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown member author %s' % memberName}

    try:
      mapping = self.dbSession.query(AuthorGroupMap).filter(and_(AuthorGroupMap.author_group_id==authorGroupId,AuthorGroupMap.author_id==memberId)).one()
    except NoResultFound:
      self.request.response.status_int = 404
      return {'error':'unknown member %s in group %s for author %s' % (memberName,groupName,authorName)}

    self.dbSession.delete(mapping)
    
    self.dbSession.commit()  
  
    return mapping.toJSONObject()
