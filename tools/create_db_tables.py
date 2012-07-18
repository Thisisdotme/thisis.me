#!/usr/bin/env python

import sys
import logging

from tim_commons.app_base import AppBase
from tim_commons import db

import mi_schema.models as mi_schema


class CreateDBTables(AppBase):

  def app_main(self, config, options, args):

    logging.info("Beginning...")

    # initialize the db engine & session
    db.configure_session(url=db.create_url_from_config(config['db']))

    # get the engine, bind it to the metadata base, and create
    # the tables
    engine = db.Session().get_bind()

    mi_schema.Base.metadata.bind = engine
    mi_schema.Base.metadata.create_all(engine)

    logging.info("Finished...")

if __name__ == '__main__':
  # Initialize with number of arguments script takes
  sys.exit(CreateDBTables('create_db_tables').main())
