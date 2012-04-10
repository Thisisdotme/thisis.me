# define the root location for all mobile identity scripts, source, config files, etc.
export MI_HOME=~/dev

# define location of configuration files
export MI_CONFIG=$MI_HOME/config

export MI_OAUTH_KEYS=$MI_CONFIG/oauth_keys.test.json

# define the pythonpath
export PYTHONPATH=$MI_HOME/mi-utils:$MI_HOME/mi-model:$MI_HOME/mi-db:$MI_HOME/mi-collectors

# define s3 scripts bucket
export SCRIPT_BUCKET=scripts.dev.thisis.me
