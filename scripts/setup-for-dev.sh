#!/bin/bash

set -ex

# Prepare environment

# Assume brew, python 3.8+, poetry, gem, and docker are already present
# Will modify globals nonetheless.

brew install shellcheck
brew install cloc
brew install create-dmg
poetry install --no-interaction --no-ansi
sudo gem install mdl
docker pull hadolint/hadolint:latest-debian
