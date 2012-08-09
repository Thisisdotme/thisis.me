'''
Created on Feb 21, 2012

@author: howard
'''

import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from tim_commons import db

from mi_schema.models import Author, AuthorGroup, AuthorGroupMap

import miapi.resource


def add_views(configuration):
  # AuthorGroups
  configuration.add_view(
      list_author_groups,
      context=miapi.resource.AuthorGroups,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_author_group,
      context=miapi.resource.AuthorGroups,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # AuthorGroup
  configuration.add_view(
      get_author_group,
      context=miapi.resource.AuthorGroup,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_author_group,
      context=miapi.resource.AuthorGroup,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)

  # AuthorGroupMembers
  configuration.add_view(
      list_author_group_members,
      context=miapi.resource.AuthorGroupMembers,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      add_author_group_member,
      context=miapi.resource.AuthorGroupMembers,
      request_method='POST',
      permission='create',
      renderer='jsonp',
      http_cache=0)

  # AuthorGroupMembers
  configuration.add_view(
      get_author_group_member,
      context=miapi.resource.AuthorGroupMember,
      request_method='GET',
      permission='read',
      renderer='jsonp',
      http_cache=0)
  configuration.add_view(
      delete_author_group_member,
      context=miapi.resource.AuthorGroupMember,
      request_method='DELETE',
      permission='write',
      renderer='jsonp',
      http_cache=0)


# GET /v1/authors/{authorname}/groups
#
# return all authors that match the specified search criteria
#
def list_author_groups(context, request):

  author = context.author

  db_session = db.Session()

  groupList = []
  for group in db_session.query(AuthorGroup).filter(AuthorGroup.author_id == author.id).order_by(AuthorGroup.group_name):
    groupList.append(group.to_JSON_dictionary())

  return {'author_name': author.author_name, 'groups': groupList}


# POST /v1/authors/{authorname}/groups
#
def add_author_group(context, request):

  author = context.author

  group_info = request.json_body

  group_name = group_info.get('name')
  if group_name is None:
    request.response.status_int = 400
    return {'error': 'missing required property: name'}

  db_session = db.Session()

  author_group = AuthorGroup(author.id, group_name)

  try:
    db_session.add(author_group)
    db_session.flush()

    logging.info('created author_group: "{name}"'.format(name=group_name))

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

  return author_group.to_JSON_dictionary()


# GET /v1/authors/{authorname}/groups/{groupname}
#
def get_author_group(context, request):
  return context.author_group.to_JSON_dictionary()


# DELETE /v1/authors/{authorname}/groups/{groupname}
#
def delete_author_group(context, request):

  author_group = context.author_group

  if author_group.group_name == 'follow':
    request.response.status_int = 403
    return {'error': 'cannot delete the required group "{name}"'.format(name=author_group.group_name)}

  db_session = db.Session()
  db_session.delete(author_group)
  db_session.flush()

  return author_group.to_JSON_dictionary()


# GET /v1/authors/{authorname}/groups/{groupname}/members
#
def list_author_group_members(context, request):

  author = context.author
  author_group = context.author_group

  memberList = []
  for member in db.Session().query(AuthorGroupMap).join(Author). \
                               filter(Author.id == AuthorGroupMap.author_id). \
                               filter(AuthorGroupMap.author_group_id == author_group.id). \
                               order_by(Author.author_name):
    memberList.append(member.to_JSON_dictionary(author, author_group))

  responseJSON = author_group.to_JSON_dictionary()
  responseJSON['author_name'] = author.author_name
  responseJSON['members'] = memberList

  return responseJSON


# POST /v1/authors/{authorname}/groups/{groupname}/members/{member}
#
def add_author_group_member(context, request):

  author = context.author
  author_group = context.author_group

  group_info = request.json_body

  member_name = group_info.get('name')
  if member_name is None:
    request.response.status_int = 400
    return {'error': 'missing required property: name'}

  db_session = db.Session()
  try:
    member = db_session.query(Author).filter_by(author_name=member_name).one()
  except NoResultFound:
    request.response.status_int = 404
    return {'error': 'unknown member author %s' % member_name}

  mapping = AuthorGroupMap(author_group.id, member.id)

  try:
    db_session.add(mapping)
    db_session.flush()

    logging.info("Added {member} to {author}'s author_group {group}".format(member=member.author_name,
                                                                            author=author.author_name,
                                                                            group=author_group.group_name))

  except IntegrityError, e:
    request.response.status_int = 409
    return {'error': e.message}

  return mapping.to_JSON_dictionary(author, author_group)


# GET /v1/authors/{authorname}/groups/{groupname}/members/{member}
#
def get_author_group_member(context, request):

  author = context.author
  author_group = context.author_group
  member = context.author_group_member

  return member.to_JSON_dictionary(author, author_group)


# DELETE /v1/authors/{authorname}/groups/{groupname}/members/{member}
#
def delete_author_group_member(context, request):

  db_session = db.Session()
  db_session.delete(context.author_group_member)

  return context.author_group_member.to_JSON_dictionary(context.author, context.author_group)
