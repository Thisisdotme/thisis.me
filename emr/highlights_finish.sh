#!/usr/bin/env bash

# environment setup
. /opt/mi/env/bin/activate                                                                                                                                             
. /opt/mi/config/environment.sh
export PATH=$PATH:/opt/emr

# finish jobs

# finish foursquare
ATTEMPT=1
while [  $ATTEMPT -lt 4 ]; do
	echo Foursquare rendezvous attempt $ATTEMPT
	let ATTEMPT=ATTEMPT+1 
	/opt/mi/emr/foursquare_finish.py
	if [ $? -eq 0 ]; then
		break
	fi
	# sleep for 5 minutes before retrying
	sleep 5m
done

# abort if more than 3 attempts
if [ $ATTEMPT -ge 4 ]; then
	exit 1
fi

# finish twitter
ATTEMPT=1
while [  $ATTEMPT -lt 4 ]; do
	echo Twitter rendezvous attempt $ATTEMPT
	let ATTEMPT=ATTEMPT+1 
	/opt/mi/emr/twitter_finish.py
	if [ $? -eq 0 ]; then
		break
	fi
	# sleep for 5 minutes before retrying
	sleep 5m
done

# abort if more than 3 attempts
if [ $ATTEMPT -ge 4 ]; then
	exit 1
fi

# finish linkedin
ATTEMPT=1
while [  $ATTEMPT -lt 4 ]; do
	echo LinkedIn rendezvous attempt $ATTEMPT
	let ATTEMPT=ATTEMPT+1 
	/opt/mi/emr/linkedin_finish.py
	if [ $? -eq 0 ]; then
		break
	fi
	# sleep for 5 minutes before retrying
	sleep 5m
done

# abort if more than 3 attempts
if [ $ATTEMPT -ge 4 ]; then
	exit 1
fi