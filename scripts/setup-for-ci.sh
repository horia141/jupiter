#!/bin/bash

set -ex

# Prepare environment

source .venv/bin/activate
poetry install --no-interaction --no-ansi
gem install mdl
docker pull hadolint/hadolint:latest-debian
