#!/bin/bash

set -ex

# Prepare environment

# Assume brew, python 3.10+, ruby 3.3.x+, JDK, gcloud cli, poetry, node, gem,
# npm, npx, bundler, gh (the GitHub command line), cocoapods, Android Studio,
# XCode, and Docker are already present.
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
(cd src/cli && poetry install --no-interaction --no-ansi)
(cd src/webapi && poetry install --no-interaction --no-ansi)
(cd src/core && poetry install --no-interaction --no-ansi)
(cd tests && poetry install --no-interaction --no-ansi)
npm install --ws --include-workspace-root
(cd src/desktop && npm install --no-ansi)
(cd src/mobile && npm install --no-ansi)

playwright install
(cd gen/ts/webapi-client && npx tsc)
