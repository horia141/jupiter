#!/bin/bash

set -e

# Prepare environment

brew install shellcheck
pip install -r requirements-dev.txt
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian

# Prepare dependencies

pip install -r requirements.txt
