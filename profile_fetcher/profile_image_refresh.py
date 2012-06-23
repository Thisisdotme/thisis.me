#!/usr/bin/env python

import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons import db

from profile_fetchers import profile_fetcher
from mi_schema.models import (Service, AuthorServiceMap)


class ProfileImageRefreshDriver(AppBase):

  def init_args(self, option_parser):
    option_parser.add_option('--service',
                             dest='services',
                             action='append',
                             default=[],
                             help='Services to process')

  def app_main(self, config, options, args):

    logging.info("Beginning...")

    # read the db url from the config
    db_url = config['db']['sqlalchemy.url']

    # initialize the db engine & session
    db.configure_session(db_url)

    # if services option is empty default to all available configured services
    if not options.services:
      service_names = []
      # generate the list of service name's from queue list
      for key in config['queues'].iterkeys():
        service_names.append(key)
    else:
      service_names = options.services

    # for each specified service
    for service_name in service_names:

      fetcher = profile_fetcher.from_service_name(service_name, config['oauth'][service_name])

      # get each author subscribed to this service
      for asm in db.Session().query(AuthorServiceMap). \
                              join(Service, AuthorServiceMap.service_id == Service.id). \
                              filter(Service.service_name == service_name).all():

        profile_json = fetcher.get_author_profile(asm.service_author_id, asm)

        if 'picture_url' in profile_json:
          asm.profile_image_url = profile_json['picture_url']
          db.Session().flush()

    logging.info("Finished...")

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(ProfileImageRefreshDriver('profile_image_refresh').main())
