#!/usr/bin/env bash

cd $TIM_HOME

api_tar_file=api.tar.gz
mobile_tar_file=poc.tar.gz
collector_tar_file=collector.tar.gz

# Remove all the tar files
rm -f $api_tar_file
rm -f $mobile_tar_file
rm -f $collector_tar_file

tar -zcf $api_tar_file config/ mi-api/ mi-db/ mi-model/ mi-utils/ mi-model/ mi-traversal/ emr/
tar -zcf $mobile_tar_file config/ mi-db/ mi-model/ mi-utils/ tim-web/ tim-viewer/ tim-mobile/
tar -zcf $collector_tar_file config event-collector even-interpreter event-processor \
                             event-updator tim-commons tim-feed event-scanner \
