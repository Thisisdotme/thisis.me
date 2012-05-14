import os
import logging

from configobj import ConfigObj


def load_configuration(config_file):
  def recursive_load_configuration(config, config_file):
    TIM_CONFIG_KEY = {'TIM_CONFIG': os.environ['TIM_CONFIG']}
    config_file = config_file.format(**TIM_CONFIG_KEY)
    logging.info('Processing file: {0}'.format(config_file))

    if not os.path.exists(config_file):
      raise Exception('Could not find the configuration file: {0}'.format(config_file))

    topConfig = ConfigObj(config_file, interpolation=False)

    # load the configs for the include section
    merge_configs = []
    include = topConfig.get('include', {})
    for value in include.itervalues():
      merge_configs.append(recursive_load_configuration(config, value))

    # remove the include section
    topConfig.pop('include', None)

    for included_config in merge_configs:
      config.merge(included_config)
    config.merge(topConfig)

    return config

  return recursive_load_configuration(ConfigObj(), config_file)


ENVIRONMENT_KEY = 'environment'


def update_pyramid_configuration(settings):
  environment_config_file = settings.get('environment_file', '{TIM_CONFIG}/config.ini')
  environment_config = load_configuration(environment_config_file)

  if ENVIRONMENT_KEY in settings:
    raise Exception('Setting dictionary already contains an environment key')
  else:
    settings[ENVIRONMENT_KEY] = environment_config
