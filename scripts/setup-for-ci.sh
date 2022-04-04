#!/bin/bash

set -e

# Prepare environment

poetry install --no-interaction --no-ansi
gem install mdl
docker pull hadolint/hadolint:latest-debian
