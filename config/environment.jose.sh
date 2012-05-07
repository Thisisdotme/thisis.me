# define the root location for all mobile identity scripts, sourcec code, config
# files, etc.
export MI_HOME=/home/jose/dev/work/thisis.me

# define location of configuration files
export MI_CONFIG=$MI_HOME/config

# define oath keys
export MI_OAUTH_KEYS=$MI_CONFIG/oauth_keys.jose.json

# define the pythonpath
export PYTHONPATH=$MI_HOME/mi-utils:$MI_HOME/mi-model:$MI_HOME/mi-db
export PYTHONPATH=$MI_HOME/mi-collectors:$MI_HOME/mi-traversal:$PYTHONPATH
export PYTHONPATH=$MI_HOME/tools:$MI_HOME/tim-commons:$PYTHONPATH

# define s3 scripts bucket
# TODO: create a script bucket for below
export SCRIPT_BUCKET=scripts.jose.thisis.me
