#!/bin/bash

set -ex

poetry run autoflake --config=scripts/check/lint/autoflake src/core src/cli src/webapi itests
poetry run black src/core src/cli src/webapi itests
poetry run ruff check --cache-dir=.build-cache/ruff --config=./scripts/check/lint/ruff.toml src itests --fix
npx prettier --write --list-different src/webui src/desktop src/mobile
npx eslint src/webui --fix
