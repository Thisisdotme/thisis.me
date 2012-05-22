#!/usr/bin/env bash

cd ~/dev

. package.sh

scp api.tar.gz ec2-user@api.thisis.me:
scp poc.tar.gz ec2-user@poc.thisis.me:
