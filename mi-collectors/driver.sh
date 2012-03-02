#!/usr/bin/env bash

source /opt/mi/env/bin/activate
source /opt/mi/config/environment.sh

pushd /opt/mi/mi-collectors
./driver.py --incremental
popd