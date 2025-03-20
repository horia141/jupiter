#!/bin/bash

set -ex

# Prepare environment

# sudo apt update (perhaps)
sudo apt-get install -y libasound2-dev

poetry config virtualenvs.create false
poetry config virtualenvs.in-project false

docker pull hadolint/hadolint:latest-debian

bundle install

poetry install --no-interaction --no-ansi
(cd src/core && poetry install --no-interaction --no-ansi)
(cd src/cli && poetry install --no-interaction --no-ansi)
(cd src/webapi && poetry install --no-interaction --no-ansi)
(cd itests && poetry install --no-interaction --no-ansi)

npm ci --ws --include-workspace-root
(cd src/desktop && npm install --no-ansi)
(cd src/mobile && npm install --no-ansi)

playwright install

(cd gen/ts/webapi-client && npx tsc)
