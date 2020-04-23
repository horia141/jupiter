#!/bin/bash

set -e

# Prepare environment

apt-get install python3-setuptools gnupg2
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
gem install mdl
docker pull hadolint/hadolint:latest-debian

# Prepare dependencies

pip install -r requirements.txt
