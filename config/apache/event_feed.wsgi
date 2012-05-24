import os, sys

from pyramid import paster

TIM_HOME = os.environ['TIM_HOME']
INIFILE = os.path.join(TIM_HOME, 'event-feed/development.ini')

os.environ['PYTHON_EGG_CACHE'] = '/var/tmp'

application = paster.get_app(INIFILE 'main')
paster.setup_logging(INIFILE)
