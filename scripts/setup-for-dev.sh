#!/bin/bash

set -e

brew install shellcheck
curl -sSL https://get.rvm.io | bash -s stable
rvm install ruby-2.4.2
sudo pip3 install pylint yamllint
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian