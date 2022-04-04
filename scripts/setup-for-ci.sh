#!/bin/bash

set -ex

# Prepare environment

poetry install --no-interaction --no-ansi
gem install mdl
docker pull hadolint/hadolint:latest-debian
