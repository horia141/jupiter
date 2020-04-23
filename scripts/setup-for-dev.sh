#!/bin/bash

set -e

# Prepare environment

brew install shellcheck
gpg2 --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
curl -sSL https://get.rvm.io | bash -s stable
rvm install ruby-2.4.2
python -m pip install --upgrade pip
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian

# Prepare dependencies

pip install -r requirements.txt
