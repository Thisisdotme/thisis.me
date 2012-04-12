#!/usr/bin/env bash

s3cmd put foursquare_dedup_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put foursquare_dedup_reducer.py s3://$SCRIPT_BUCKET/

s3cmd put foursquare_30d_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put foursquare_checkin_aggregator_reducer.py s3://$SCRIPT_BUCKET/

s3cmd put foursquare_minmax_reducer.py s3://$SCRIPT_BUCKET/

s3cmd put foursquare_highlight_reducer.py s3://$SCRIPT_BUCKET/

