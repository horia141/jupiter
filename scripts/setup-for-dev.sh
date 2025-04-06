#!/bin/bash

set -ex

# Prepare environment

# Assume brew, python 3.13+, ruby 3.3.x+, JDK, gcloud cli, poetry, node, gem,
# npm, npx, bundler, gh (the GitHub command line), cocoapods, Android Studio,
# XCode, rust, cargo, and Docker are already present.
# Will modify globals nonetheless.

mkdir -p .build-cache
python3 -m venv .build-cache/venv
source .build-cache/venv/bin/activate

# brew install shellcheck
brew install cloc
brew install create-dmg
docker pull hadolint/hadolint:latest-debian

bundle install

poetry install --no-interaction --no-ansi
(cd src/core && poetry install --no-interaction --no-ansi)
(cd src/cli && poetry install --no-interaction --no-ansi)
(cd src/webapi && poetry install --no-interaction --no-ansi)
(cd src/docs && poetry install --no-interaction --no-ansi)
(cd itests && poetry install --no-interaction --no-ansi)

npm install --no-save
(cd src/desktop && npm install --no-save)
(cd src/mobile && npm install --no-save)

playwright install

(cd gen/ts/webapi-client && npx tsc)
