#!/bin/bash

set -e

# Prepare environment

poetry install --no-interactive --no-ansi
gem install mdl
docker pull hadolint/hadolint:latest-debian
