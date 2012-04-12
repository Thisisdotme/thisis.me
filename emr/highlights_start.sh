#!/usr/bin/env bash

# environment setup
. /opt/mi/env/bin/activate                                                                                                                                             
. /opt/mi/config/environment.sh
export PATH=$PATH:/opt/emr

# create new emr job
tokens=( `elastic-mapreduce --create` )

# get job id
jobId=${tokens[`expr ${#tokens[@]} - 1`]}

# start jobs
/opt/mi/emr/foursquare_start.py $jobId
/opt/mi/emr/twitter_start.py $jobId
/opt/mi/emr/linkedin_start.py $jobId
