environment=cameron
export TIM_USER=design

# Define the python egg cache. Let just use the user's home directory
export PYTHON_EGG_CACHE=$(getent passwd $TIM_USER | cut -d: -f6)/.python-eggs

# Define the root location for all mobile identity scripts, sourcec code, config
# files, etc.
export TIM_HOME=/Users/design/dev/thisis.me

# Soure the python virtual environment
. $TIM_HOME/env/bin/activate

# Define root location for data file
export TIM_DATA=$TIM_HOME/data/$environment

# Define location of configuration files
export TIM_CONFIG=$TIM_HOME/config/$environment

# Define oath keys
export TIM_OAUTH_KEYS=$TIM_CONFIG/oauth_keys.json

# Define the pythonpath
export PYTHONPATH=$TIM_HOME/mi-model:$TIM_HOME/mi-db
export PYTHONPATH=$TIM_HOME/tools:$TIM_HOME/commons:$TIM_HOME/event_scanner:$TIM_HOME/profile_fetcher:$PYTHONPATH

# define s3 scripts bucket
export SCRIPT_BUCKET=scripts.dev.thisis.me
