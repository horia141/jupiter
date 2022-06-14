#!/bin/bash

set -e

# Prepare environment

brew install shellcheck
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
# shellcheck disable=SC1090 # poetry is special here
~/.poetry/bin/poetry install --no-interaction --no-ansi
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian
