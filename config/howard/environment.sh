environment=howard
export TIM_USER=howard

# Define the python egg cache. Let just use the user's home directory
command -v getent >/dev/null 2>&1
status=$?
if [ $status -ne 0 ]; then
  # if getent doesn't exist then assume we are using Mac OS X
  export PYTHON_EGG_CACHE=/Users/$TIM_USER/.python-eggs
else
  export PYTHON_EGG_CACHE=$(getent passwd $TIM_USER | cut -d: -f6)/.python-eggs
fi

# Define the root location for all mobile identity scripts, sourcec code, config
# files, etc.
export TIM_HOME=/Users/howard/dev/thisis.me

# Soure the python virtual environment
. $TIM_HOME/env/bin/activate

# Define root location for data file
export TIM_DATA=$TIM_HOME/data/$environment

# Define location of configuration files
export TIM_CONFIG=$TIM_HOME/config/$environment

# Define oath keys
export TIM_OAUTH_KEYS=$TIM_CONFIG/oauth_keys.json

# Define the pythonpath
export PYTHONPATH=$TIM_HOME/tools:$TIM_HOME/commons:$TIM_HOME/event_scanner:$TIM_HOME/profile_fetcher:$PYTHONPATH

# define s3 scripts bucket
export SCRIPT_BUCKET=scripts.dev.thisis.me
