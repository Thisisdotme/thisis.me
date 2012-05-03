# define the root location for all mobile identity scripts, source, config files, etc.
export MI_HOME=/opt/mi
export TIM_HOME=/opt/mi

# define location of configuration files
export MI_CONFIG=$MI_HOME/config
export TIM_CONFIG=$TIM_HOME/config

export MI_OAUTH_KEYS=$MI_CONFIG/oauth_keys.json
export TIM_OAUTH_KEYS=$TIM_CONFIG/oauth_keys.json

# define the pythonpath
export PYTHONPATH=$TIM_HOME/mi-utils:$TIM_HOME/mi-db:$TIM_HOME/mi-collectors:$TIM_HOME/mi-model


# define s3 scripts bucket
export SCRIPT_BUCKET=scripts.v1.thisis.me