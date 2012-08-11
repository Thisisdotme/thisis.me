import sys
import passlib.hash

import tim_commons.app_base
import tim_commons.db
import data_access.author


class EncryptPassword(tim_commons.app_base.AppBase):
  def app_main(self, config, options, args):
    tim_commons.db.configure_session(tim_commons.db.create_url_from_config(config['db']))

    authors = data_access.author.query_authors()
    for author in authors:
      print 'Do you want to encrypt the password for the author:'
      print 'name =', author.author_name, 'password =', author.password
      answer = raw_input('y/N? ')

      if answer == 'y':
        author.password = passlib.hash.sha256_crypt.encrypt(author.password)
      elif answer == 'n':
        # skip this author
        pass
      else:
        print 'Unknown answer; skipping author'

    tim_commons.db.Session().flush()


if __name__ == '__main__':
  sys.exit(EncryptPassword('encrypt_password').main())
