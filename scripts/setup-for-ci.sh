#!/bin/bash

set -echo

# Prepare dependencies

apt-get install python3-setuptools
curl -sSL https://get.rvm.io | bash -s stable
rvm install ruby-2.4.2
pip3 install pylint yamllint pyflakes bandit
gem install mdl
docker pull hadolint/hadolint:latest-debian

# Prepare environment

pip3 install -r requirements.txt
