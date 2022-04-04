#!/bin/bash

set -e

# Prepare environment

brew install shellcheck
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
poetry install --no-interaction --no-ansi
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian
