#!/bin/bash

set -ex

# Prepare environment

poetry config virtualenvs.create false
poetry config virtualenvs.in-project false

docker pull hadolint/hadolint:latest-debian

bundle install

poetry install --no-interaction --no-ansi
(cd src/core && poetry install --no-interaction --no-ansi)
(cd src/cli && poetry install --no-interaction --no-ansi)
(cd src/webapi && poetry install --no-interaction --no-ansi)
(cd tests && poetry install --no-interaction --no-ansi)

npm ci --ws --include-workspace-root
(cd gen && npx tsc)
