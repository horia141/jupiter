#!/bin/bash

set -e

# Prepare environment

brew install shellcheck
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
