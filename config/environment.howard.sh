# define the root location for all mobile identity scripts, source, config files, etc.
export MI_HOME=~/dev
export TIM_HOME=~/dev
export TIM_DATA=~/dev/data/howard

# define location of configuration files
export MI_CONFIG=$MI_HOME/config
export TIM_CONFIG=$TIM_HOME/config

export MI_OAUTH_KEYS=$TIM_CONFIG/oauth_keys.test.json

# define the pythonpath
export PYTHONPATH=$TIM_HOME/tim-commons:$TIM_HOME/mi-model:$TIM_HOME/mi-db:$TIM_HOME/mi-collectors

# define s3 scripts bucket
export SCRIPT_BUCKET=scripts.dev.thisis.me
