#!/usr/bin/env bash

s3cmd put linkedin_30d_connection_mapper.py s3://$SCRIPT_BUCKET/

s3cmd put linkedin_highlight_reducer.py s3://$SCRIPT_BUCKET/

