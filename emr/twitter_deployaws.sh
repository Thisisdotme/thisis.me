#!/usr/bin/env bash

# deduping
s3cmd put twitter_dedup_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put twitter_dedup_reducer.py s3://$SCRIPT_BUCKET/

# finding min/max retweets
s3cmd put 30d_age_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put twitter_minmax_reducer.py s3://$SCRIPT_BUCKET/

# analyizing
s3cmd put twitter_highlight_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put twitter_highlight_reducer.py s3://$SCRIPT_BUCKET/

