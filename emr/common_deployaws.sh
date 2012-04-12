#!/usr/bin/env bash

s3cmd put identity_reducer.py s3://$SCRIPT_BUCKET/
s3cmd put identity_mapper.py s3://$SCRIPT_BUCKET/

s3cmd put dedup_mapper.py s3://$SCRIPT_BUCKET/
s3cmd put dedup_reducer.py s3://$SCRIPT_BUCKET/
