environment=jose

# Define the root location for all mobile identity scripts, sourcec code, config
# files, etc.
export TIM_HOME=/home/jose/dev/work/thisis.me

# Soure the python virtual environment
. $TIM_HOME/env/bin/activate

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
export PYTHONPATH=$TIM_HOME/event_interpreter:$TIM_HOME/event_feed:$PYTHONPATH
