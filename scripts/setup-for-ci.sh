#!/bin/bash

set -echo

apt-get install python3-setuptools
curl -sSL https://get.rvm.io | bash -s stable
rvm install ruby-2.4.2
pip3 install pylint yamllint
gem install mdl
docker pull hadolint/hadolint:latest-debian