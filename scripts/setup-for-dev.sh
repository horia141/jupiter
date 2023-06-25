#!/bin/bash

set -ex

# Prepare environment

# Assume brew, python 3.10+, poetry, gem, npm, npx, bundler, and docker are already present
# Will modify globals nonetheless.

# brew install shellcheck
brew install cloc
brew install create-dmg
docker pull hadolint/hadolint:latest-debian

# gem install mdl # TODO(revert this to bundler with local install)

poetry install --no-interaction --no-ansi
(cd src/cli && poetry install --no-interaction --no-ansi)
(cd src/webapi && poetry install --no-interaction --no-ansi)
(cd src/core && poetry install --no-interaction --no-ansi)
(cd tests && poetry install --no-interaction --no-ansi)
npm install --ws --include-workspace-root
