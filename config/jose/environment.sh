environment=jose
export TIM_USER=jose

# Define the python egg cache. Let just use the user's home directory
command -v getent >/dev/null 2>&1
RETURN_VALUE=$?
if [ $RETURN_VALUE -ne 0 ]; then
  # if getent doesn't exist then assume we are using Mac OS X
  export PYTHON_EGG_CACHE=/Users/$TIM_USER/.python-eggs
else
  export PYTHON_EGG_CACHE=$(getent passwd $TIM_USER | cut -d: -f6)/.python-eggs
fi

# Define the root location for all mobile identity scripts, sourcec code, config
# files, etc.
export TIM_HOME=/home/jose/dev/work/thisis.me

# Soure the python virtual environment
source $TIM_HOME/env/bin/activate

# Define root location for data file
export TIM_DATA=$TIM_HOME/data/$environment

# Define location of configuration files
export TIM_CONFIG=$TIM_HOME/config/$environment

# Define oath keys
export TIM_OAUTH_KEYS=$TIM_CONFIG/oauth_keys.json

# Define the pythonpath
export PYTHONPATH=$TIM_HOME/mi-utils:$TIM_HOME/mi-model:$TIM_HOME/mi-db
export PYTHONPATH=$TIM_HOME/mi-collectors:$TIM_HOME/mi-traversal:$PYTHONPATH
export PYTHONPATH=$TIM_HOME/tools:$TIM_HOME/commons:$TIM_HOME/event_scanner:$PYTHONPATH
export PYTHONPATH=$TIM_HOME/event_feed:$TIM_HOME/event_processor:$PYTHONPATH
export PYTHONPATH=$TIM_HOME/profile_fetcher:$PYTHONPATH
