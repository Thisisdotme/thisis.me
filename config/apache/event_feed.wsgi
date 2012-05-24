import os, sys

from pyramid import paster

BASEDIR = os.path.dirname(__file__)
INIFILE = os.path.join(BASEDIR, 'development.ini')

os.environ['PYTHON_EGG_CACHE'] = '/var/tmp'

application = paster.get_app(INIFILE 'main')
paster.setup_logging(INIFILE)
